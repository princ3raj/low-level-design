"""Review and Rating domain models"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..value_objects import Rating


@dataclass
class Review:
    """Review entity for restaurants and deliveries"""
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    order_id: str = ""
    restaurant_id: Optional[str] = None
    delivery_partner_id: Optional[str] = None
    rating: Rating = field(default_factory=lambda: Rating(5.0))
    comment: str = ""
    food_rating: Optional[Rating] = None
    delivery_rating: Optional[Rating] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_verified: bool = False  # Verified if customer actually ordered
    
    def verify(self):
        """Mark review as verified"""
        self.is_verified = True
    
    def is_restaurant_review(self) -> bool:
        """Check if this is a restaurant review"""
        return self.restaurant_id is not None
    
    def is_delivery_review(self) -> bool:
        """Check if this is a delivery partner review"""
        return self.delivery_partner_id is not None
