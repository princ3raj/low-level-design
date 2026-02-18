"""Restaurant and Menu domain models"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..value_objects import Location, Money, Rating


@dataclass
class MenuItem:
    """Menu item entity"""
    id: str = field(default_factory=lambda: str(uuid4()))
    category_id: str = ""
    name: str = ""
    description: str = ""
    price: Money = field(default_factory=lambda: Money(0.0))
    is_available: bool = True
    is_vegetarian: bool = True
    preparation_time_minutes: int = 15
    image_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def mark_unavailable(self):
        """Mark item as unavailable"""
        self.is_available = False
    
    def mark_available(self):
        """Mark item as available"""
        self.is_available = True


@dataclass
class MenuCategory:
    """Menu category entity"""
    id: str = field(default_factory=lambda: str(uuid4()))
    restaurant_id: str = ""
    name: str = ""
    description: str = ""
    display_order: int = 0
    items: List[MenuItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_item(self, item: MenuItem):
        """Add menu item to category"""
        item.category_id = self.id
        self.items.append(item)
    
    def remove_item(self, item_id: str):
        """Remove menu item from category"""
        self.items = [item for item in self.items if item.id != item_id]
    
    def get_available_items(self) -> List[MenuItem]:
        """Get all available items in category"""
        return [item for item in self.items if item.is_available]


@dataclass
class Restaurant:
    """Restaurant entity"""
    id: str = field(default_factory=lambda: str(uuid4()))
    owner_id: str = ""
    name: str = ""
    description: str = ""
    location: Optional[Location] = None
    cuisine_types: List[str] = field(default_factory=list)
    menu_categories: List[MenuCategory] = field(default_factory=list)
    is_active: bool = True
    rating: Rating = field(default_factory=lambda: Rating(5.0))
    total_reviews: int = 0
    opening_time: str = "09:00"
    closing_time: str = "22:00"
    minimum_order_amount: Money = field(default_factory=lambda: Money(100.0))
    delivery_fee: Money = field(default_factory=lambda: Money(40.0))
    average_preparation_time: int = 30  # minutes
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_category(self, category: MenuCategory):
        """Add menu category to restaurant"""
        category.restaurant_id = self.id
        self.menu_categories.append(category)
    
    def remove_category(self, category_id: str):
        """Remove menu category from restaurant"""
        self.menu_categories = [
            cat for cat in self.menu_categories if cat.id != category_id
        ]
    
    def get_menu_item(self, item_id: str) -> Optional[MenuItem]:
        """Find menu item by ID across all categories"""
        for category in self.menu_categories:
            for item in category.items:
                if item.id == item_id:
                    return item
        return None
    
    def update_rating(self, new_rating: float):
        """Update restaurant rating with new review"""
        current_total = self.rating.value * self.total_reviews
        new_total = current_total + new_rating
        self.total_reviews += 1
        self.rating = Rating(new_total / self.total_reviews)
    
    def is_accepting_orders(self) -> bool:
        """Check if restaurant is currently accepting orders"""
        return self.is_active
    
    def deactivate(self):
        """Deactivate restaurant"""
        self.is_active = False
    
    def activate(self):
        """Activate restaurant"""
        self.is_active = True
