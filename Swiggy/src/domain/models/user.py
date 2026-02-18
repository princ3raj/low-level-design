"""User domain models"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from ..enums import UserRole, VehicleType, SubscriptionPlan
from ..value_objects import Location


@dataclass
class User:
    """Base user entity"""
    id: str = field(default_factory=lambda: str(uuid4()))
    email: str = ""
    phone: str = ""
    name: str = ""
    role: UserRole = UserRole.CUSTOMER
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class Customer(User):
    """Customer entity extending User"""
    addresses: List[Location] = field(default_factory=list)
    loyalty_points: int = 0
    subscription_plan: SubscriptionPlan = SubscriptionPlan.NONE
    subscription_expiry: Optional[datetime] = None
    
    def __post_init__(self):
        self.role = UserRole.CUSTOMER
    
    def has_active_subscription(self) -> bool:
        """Check if customer has an active subscription"""
        if self.subscription_plan == SubscriptionPlan.NONE:
            return False
        if self.subscription_expiry is None:
            return False
        return datetime.now() < self.subscription_expiry
    
    def add_loyalty_points(self, points: int):
        """Add loyalty points to customer account"""
        self.loyalty_points += points
    
    def redeem_loyalty_points(self, points: int) -> bool:
        """Redeem loyalty points, return True if successful"""
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            return True
        return False


@dataclass
class RestaurantOwner(User):
    """Restaurant owner entity"""
    restaurant_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.role = UserRole.RESTAURANT_OWNER


@dataclass
class DeliveryPartner(User):
    """Delivery partner entity"""
    current_location: Optional[Location] = None
    vehicle_type: VehicleType = VehicleType.MOTORCYCLE
    is_available: bool = True
    current_order_id: Optional[str] = None
    rating: float = 5.0
    total_deliveries: int = 0
    
    def __post_init__(self):
        self.role = UserRole.DELIVERY_PARTNER
    
    def assign_order(self, order_id: str):
        """Assign an order to this delivery partner"""
        self.current_order_id = order_id
        self.is_available = False
    
    def complete_delivery(self):
        """Mark delivery as complete and make partner available"""
        self.current_order_id = None
        self.is_available = True
        self.total_deliveries += 1
    
    def update_location(self, location: Location):
        """Update current location of delivery partner"""
        self.current_location = location
    
    def update_rating(self, new_rating: float):
        """Update average rating (simplified)"""
        if self.total_deliveries == 0:
            self.rating = new_rating
        else:
            # Simple moving average
            total_rating = self.rating * self.total_deliveries
            total_rating += new_rating
            self.rating = total_rating / (self.total_deliveries + 1)
