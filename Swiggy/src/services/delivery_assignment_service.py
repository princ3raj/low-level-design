"""Delivery partner assignment service with strategy pattern"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.models.user import DeliveryPartner
from ..domain.models.delivery import Delivery
from ..domain.models.order import Order
from ..domain.enums import DeliveryStatus
from ..domain.exceptions import NoDeliveryPartnerAvailable
from ..repositories.user_repository import DeliveryPartnerRepository
from ..repositories.delivery_repository import DeliveryRepository
from ..repositories.order_repository import OrderRepository
from ..services.geospatial_service import GeospatialService


class PartnerAssignmentStrategy(ABC):
    """Abstract strategy for delivery partner assignment"""
    
    @abstractmethod
    def select_partner(self, partners: List[DeliveryPartner],
                       order: Order) -> Optional[DeliveryPartner]:
        """Select best partner from available partners"""
        pass


class NearestPartnerStrategy(PartnerAssignmentStrategy):
    """Assign nearest available partner"""
    
    def __init__(self, geo_service: GeospatialService):
        self.geo_service = geo_service
    
    def select_partner(self, partners: List[DeliveryPartner],
                       order: Order) -> Optional[DeliveryPartner]:
        """Select nearest partner to restaurant"""
        if not partners or not order.delivery_address:
            return None
        
        # Filter partners with location
        partners_with_location = [
            p for p in partners if p.current_location is not None
        ]
        
        if not partners_with_location:
            # Return first available partner if none have location
            return partners[0] if partners else None
        
        # Find nearest partner
        nearest_partner = min(
            partners_with_location,
            key=lambda p: self.geo_service.calculate_distance(
                order.delivery_address.latitude,
                order.delivery_address.longitude,
                p.current_location.latitude,
                p.current_location.longitude
            )
        )
        
        return nearest_partner


class RatingBasedStrategy(PartnerAssignmentStrategy):
    """Assign partner with highest rating"""
    
    def select_partner(self, partners: List[DeliveryPartner],
                       order: Order) -> Optional[DeliveryPartner]:
        """Select partner with highest rating"""
        if not partners:
            return None
        
        return max(partners, key=lambda p: p.rating)


class LoadBalancingStrategy(PartnerAssignmentStrategy):
    """Assign partner with least deliveries"""
    
    def select_partner(self, partners: List[DeliveryPartner],
                       order: Order) -> Optional[DeliveryPartner]:
        """Select partner with fewest total deliveries"""
        if not partners:
            return None
        
        return min(partners, key=lambda p: p.total_deliveries)


class DeliveryAssignmentService:
    """Service for assigning delivery partners to orders"""
    
    def __init__(self,
                 partner_repo: DeliveryPartnerRepository,
                 delivery_repo: DeliveryRepository,
                 order_repo: OrderRepository,
                 geo_service: GeospatialService,
                 strategy: Optional[PartnerAssignmentStrategy] = None):
        self.partner_repo = partner_repo
        self.delivery_repo = delivery_repo
        self.order_repo = order_repo
        self.geo_service = geo_service
        self.strategy = strategy or NearestPartnerStrategy(geo_service)
    
    def set_strategy(self, strategy: PartnerAssignmentStrategy):
        """Change assignment strategy at runtime"""
        self.strategy = strategy
    
    def assign_partner_to_order(self, order_id: str,
                                radius_km: float = 10.0) -> Delivery:
        """
        Assign a delivery partner to an order
        Uses configured strategy to select best partner
        """
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if not order.delivery_address:
            raise ValueError("Order has no delivery address")
        
        # Find available partners near restaurant
        available_partners = self.partner_repo.find_available_partners()
        
        if not available_partners:
            raise NoDeliveryPartnerAvailable("No partners currently available")
        
        # Use strategy to select best partner
        selected_partner = self.strategy.select_partner(available_partners, order)
        
        if not selected_partner:
            raise NoDeliveryPartnerAvailable()
        
        # Create delivery
        delivery = Delivery(
            order_id=order_id,
            delivery_partner_id=selected_partner.id,
            delivery_location=order.delivery_address,
            status=DeliveryStatus.ASSIGNED
        )
        
        # Update partner status
        selected_partner.assign_order(order_id)
        self.partner_repo.save(selected_partner)
        
        # Save delivery
        self.delivery_repo.save(delivery)
        
        return delivery
    
    def update_delivery_location(self, delivery_id: str,
                                 latitude: float, longitude: float) -> Delivery:
        """Update current location of delivery"""
        delivery = self.delivery_repo.find_by_id(delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        from ..domain.value_objects import Location
        location = Location(latitude=latitude, longitude=longitude)
        delivery.update_location(location)
        
        # Also update partner location
        partner = self.partner_repo.find_by_id(delivery.delivery_partner_id)
        if partner:
            partner.update_location(location)
            self.partner_repo.save(partner)
        
        self.delivery_repo.save(delivery)
        return delivery
    
    def mark_picked_up(self, delivery_id: str) -> Delivery:
        """Mark order as picked up from restaurant"""
        delivery = self.delivery_repo.find_by_id(delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        delivery.mark_picked_up()
        self.delivery_repo.save(delivery)
        
        return delivery
    
    def mark_delivered(self, delivery_id: str) -> Delivery:
        """Mark order as delivered"""
        delivery = self.delivery_repo.find_by_id(delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        delivery.mark_delivered()
        
        # Update partner status
        partner = self.partner_repo.find_by_id(delivery.delivery_partner_id)
        if partner:
            partner.complete_delivery()
            self.partner_repo.save(partner)
        
        self.delivery_repo.save(delivery)
        
        return delivery
    
    def get_delivery_by_order(self, order_id: str) -> Optional[Delivery]:
        """Get delivery information for an order"""
        return self.delivery_repo.find_by_order(order_id)
    
    def get_available_partners(self) -> List[DeliveryPartner]:
        """Get all available delivery partners"""
        return self.partner_repo.find_available_partners()
