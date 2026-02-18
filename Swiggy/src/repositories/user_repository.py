"""User repository"""
from typing import Optional, List
from .base_repository import BaseRepository
from ..domain.models.user import User, Customer, DeliveryPartner, RestaurantOwner
from ..domain.enums import UserRole


class UserRepository(BaseRepository[User]):
    """Repository for user entities"""
    
    def _get_entity_id(self, entity: User) -> str:
        return entity.id
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        for user in self._storage.values():
            if user.email == email:
                return user
        return None
    
    def find_by_phone(self, phone: str) -> Optional[User]:
        """Find user by phone number"""
        for user in self._storage.values():
            if user.phone == phone:
                return user
        return None
    
    def find_by_role(self, role: UserRole) -> List[User]:
        """Find all users by role"""
        return [user for user in self._storage.values() if user.role == role]


class CustomerRepository(BaseRepository[Customer]):
    """Repository for customer entities"""
    
    def _get_entity_id(self, entity: Customer) -> str:
        return entity.id
    
    def find_by_subscription_plan(self, plan: str) -> List[Customer]:
        """Find customers by subscription plan"""
        return [
            customer for customer in self._storage.values()
            if customer.subscription_plan.value == plan
        ]
    
    def find_active_subscribers(self) -> List[Customer]:
        """Find customers with active subscriptions"""
        return [
            customer for customer in self._storage.values()
            if customer.has_active_subscription()
        ]


class DeliveryPartnerRepository(BaseRepository[DeliveryPartner]):
    """Repository for delivery partner entities"""
    
    def _get_entity_id(self, entity: DeliveryPartner) -> str:
        return entity.id
    
    def find_available_partners(self) -> List[DeliveryPartner]:
        """Find all available delivery partners"""
        return [
            partner for partner in self._storage.values()
            if partner.is_available
        ]
    
    def find_by_location(self, latitude: float, longitude: float, 
                        radius_km: float = 10.0) -> List[DeliveryPartner]:
        """
        Find delivery partners near a location
        Uses simple distance calculation for demo
        """
        from ..services.geospatial_service import GeospatialService
        
        geo_service = GeospatialService()
        nearby_partners = []
        
        for partner in self._storage.values():
            if partner.current_location:
                distance = geo_service.calculate_distance(
                    latitude, longitude,
                    partner.current_location.latitude,
                    partner.current_location.longitude
                )
                if distance <= radius_km:
                    nearby_partners.append(partner)
        
        return nearby_partners


class RestaurantOwnerRepository(BaseRepository[RestaurantOwner]):
    """Repository for restaurant owner entities"""
    
    def _get_entity_id(self, entity: RestaurantOwner) -> str:
        return entity.id
    
    def find_by_restaurant_id(self, restaurant_id: str) -> Optional[RestaurantOwner]:
        """Find owner by restaurant ID"""
        for owner in self._storage.values():
            if restaurant_id in owner.restaurant_ids:
                return owner
        return None
