"""Restaurant service for managing restaurants and menus"""
from typing import List, Optional
from ..domain.models.restaurant import Restaurant, MenuCategory, MenuItem
from ..domain.value_objects import Location, Money
from ..domain.exceptions import RestaurantNotActive
from ..repositories.restaurant_repository import (
    RestaurantRepository,
    MenuCategoryRepository,
    MenuItemRepository
)


class RestaurantService:
    """Service for restaurant operations"""
    
    def __init__(self,
                 restaurant_repo: RestaurantRepository,
                 category_repo: MenuCategoryRepository,
                 item_repo: MenuItemRepository):
        self.restaurant_repo = restaurant_repo
        self.category_repo = category_repo
        self.item_repo = item_repo
    
    def create_restaurant(self, owner_id: str, name: str, 
                         location: Location, **kwargs) -> Restaurant:
        """Create a new restaurant"""
        restaurant = Restaurant(
            owner_id=owner_id,
            name=name,
            location=location,
            **kwargs
        )
        return self.restaurant_repo.save(restaurant)
    
    def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        """Get restaurant by ID"""
        return self.restaurant_repo.find_by_id(restaurant_id)
    
    def get_nearby_restaurants(self, latitude: float, longitude: float,
                               radius_km: float = 5.0) -> List[Restaurant]:
        """Find restaurants near a location"""
        return self.restaurant_repo.find_nearby_restaurants(
            latitude, longitude, radius_km
        )
    
    def search_restaurants(self, query: str) -> List[Restaurant]:
        """Search restaurants by name or cuisine"""
        return self.restaurant_repo.search(query)
    
    def add_menu_category(self, restaurant_id: str, name: str,
                          description: str = "") -> Optional[MenuCategory]:
        """Add a menu category to a restaurant"""
        restaurant = self.restaurant_repo.find_by_id(restaurant_id)
        if not restaurant:
            return None
        
        category = MenuCategory(
            restaurant_id=restaurant_id,
            name=name,
            description=description
        )
        
        restaurant.add_category(category)
        self.restaurant_repo.save(restaurant)
        self.category_repo.save(category)
        
        return category
    
    def add_menu_item(self, category_id: str, name: str, 
                      price: Money, **kwargs) -> Optional[MenuItem]:
        """Add a menu item to a category"""
        category = self.category_repo.find_by_id(category_id)
        if not category:
            return None
        
        item = MenuItem(
            category_id=category_id,
            name=name,
            price=price,
            **kwargs
        )
        
        category.add_item(item)
        self.category_repo.save(category)
        self.item_repo.save(item)
        
        return item
    
    def update_item_availability(self, item_id: str, is_available: bool) -> bool:
        """Update menu item availability"""
        item = self.item_repo.find_by_id(item_id)
        if not item:
            return False
        
        if is_available:
            item.mark_available()
        else:
            item.mark_unavailable()
        
        self.item_repo.save(item)
        return True
    
    def get_restaurant_menu(self, restaurant_id: str) -> List[MenuCategory]:
        """Get full menu for a restaurant"""
        return self.category_repo.find_by_restaurant(restaurant_id)
    
    def activate_restaurant(self, restaurant_id: str) -> bool:
        """Activate a restaurant"""
        restaurant = self.restaurant_repo.find_by_id(restaurant_id)
        if not restaurant:
            return False
        
        restaurant.activate()
        self.restaurant_repo.save(restaurant)
        return True
    
    def deactivate_restaurant(self, restaurant_id: str) -> bool:
        """Deactivate a restaurant"""
        restaurant = self.restaurant_repo.find_by_id(restaurant_id)
        if not restaurant:
            return False
        
        restaurant.deactivate()
        self.restaurant_repo.save(restaurant)
        return True
