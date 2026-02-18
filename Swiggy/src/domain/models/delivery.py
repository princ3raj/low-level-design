"""Delivery domain model"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..enums import DeliveryStatus
from ..value_objects import Location


@dataclass
class Delivery:
    """Delivery entity for tracking order delivery"""
    id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    delivery_partner_id: str = ""
    restaurant_location: Optional[Location] = None
    delivery_location: Optional[Location] = None
    current_location: Optional[Location] = None
    status: DeliveryStatus = DeliveryStatus.ASSIGNED
    assigned_at: datetime = field(default_factory=datetime.now)
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_distance_km: float = 0.0
    
    def update_location(self, location: Location):
        """Update current location of delivery partner"""
        self.current_location = location
    
    def mark_en_route_to_restaurant(self):
        """Update status when partner is heading to restaurant"""
        self.status = DeliveryStatus.EN_ROUTE_TO_RESTAURANT
    
    def mark_at_restaurant(self):
        """Update status when partner arrives at restaurant"""
        self.status = DeliveryStatus.AT_RESTAURANT
    
    def mark_picked_up(self):
        """Update status when order is picked up from restaurant"""
        self.status = DeliveryStatus.PICKED_UP
        self.picked_up_at = datetime.now()
    
    def mark_en_route_to_customer(self):
        """Update status when partner is heading to customer"""
        self.status = DeliveryStatus.EN_ROUTE_TO_CUSTOMER
    
    def mark_delivered(self):
        """Update status when order is delivered"""
        self.status = DeliveryStatus.DELIVERED
        self.delivered_at = datetime.now()
    
    def get_current_status_display(self) -> str:
        """Get user-friendly status message"""
        status_messages = {
            DeliveryStatus.ASSIGNED: "Delivery partner assigned",
            DeliveryStatus.EN_ROUTE_TO_RESTAURANT: "Partner is heading to restaurant",
            DeliveryStatus.AT_RESTAURANT: "Partner is at the restaurant",
            DeliveryStatus.PICKED_UP: "Order picked up",
            DeliveryStatus.EN_ROUTE_TO_CUSTOMER: "On the way to you",
            DeliveryStatus.DELIVERED: "Delivered"
        }
        return status_messages.get(self.status, "Unknown status")
