"""Restaurant repository with geospatial queries"""
from typing import List, Optional
from .base_repository import BaseRepository
from ..domain.models.restaurant import Restaurant, MenuCategory, MenuItem


class RestaurantRepository(BaseRepository[Restaurant]):
    """Repository for restaurant entities"""
    
    def _get_entity_id(self, entity: Restaurant) -> str:
        return entity.id
    
    def find_active_restaurants(self) -> List[Restaurant]:
        """Find all active restaurants"""
        return [r for r in self._storage.values() if r.is_active]
    
    def find_by_cuisine(self, cuisine_type: str) -> List[Restaurant]:
        """Find restaurants by cuisine type"""
        return [
            r for r in self._storage.values()
            if cuisine_type.lower() in [c.lower() for c in r.cuisine_types]
        ]
    
    def find_nearby_restaurants(self, latitude: float, longitude: float,
                               radius_km: float = 5.0) -> List[Restaurant]:
        """
        Find restaurants within a radius of given location
        Uses Haversine formula for distance calculation
        """
        from ..services.geospatial_service import GeospatialService
        
        geo_service = GeospatialService()
        nearby_restaurants = []
        
        for restaurant in self._storage.values():
            if not restaurant.is_active or not restaurant.location:
                continue
            
            distance = geo_service.calculate_distance(
                latitude, longitude,
                restaurant.location.latitude,
                restaurant.location.longitude
            )
            
            if distance <= radius_km:
                nearby_restaurants.append(restaurant)
        
        # Sort by distance (closest first)
        nearby_restaurants.sort(
            key=lambda r: geo_service.calculate_distance(
                latitude, longitude,
                r.location.latitude,
                r.location.longitude
            )
        )
        
        return nearby_restaurants
    
    def find_by_owner(self, owner_id: str) -> List[Restaurant]:
        """Find all restaurants owned by a specific owner"""
        return [r for r in self._storage.values() if r.owner_id == owner_id]
    
    def find_by_rating(self, min_rating: float) -> List[Restaurant]:
        """Find restaurants with rating >= min_rating"""
        return [
            r for r in self._storage.values()
            if r.rating.value >= min_rating
        ]
    
    def search(self, query: str) -> List[Restaurant]:
        """Search restaurants by name or cuisine"""
        query_lower = query.lower()
        results = []
        
        for restaurant in self._storage.values():
            if (query_lower in restaurant.name.lower() or
                any(query_lower in cuisine.lower() for cuisine in restaurant.cuisine_types)):
                results.append(restaurant)
        
        return results


class MenuCategoryRepository(BaseRepository[MenuCategory]):
    """Repository for menu categories"""
    
    def _get_entity_id(self, entity: MenuCategory) -> str:
        return entity.id
    
    def find_by_restaurant(self, restaurant_id: str) -> List[MenuCategory]:
        """Find all categories for a restaurant"""
        return [
            cat for cat in self._storage.values()
            if cat.restaurant_id == restaurant_id
        ]


class MenuItemRepository(BaseRepository[MenuItem]):
    """Repository for menu items"""
    
    def _get_entity_id(self, entity: MenuItem) -> str:
        return entity.id
    
    def find_by_category(self, category_id: str) -> List[MenuItem]:
        """Find all items in a category"""
        return [
            item for item in self._storage.values()
            if item.category_id == category_id
        ]
    
    def find_available_items(self, category_id: str) -> List[MenuItem]:
        """Find available items in a category"""
        return [
            item for item in self._storage.values()
            if item.category_id == category_id and item.is_available
        ]
    
    def find_vegetarian_items(self) -> List[MenuItem]:
        """Find all vegetarian items"""
        return [item for item in self._storage.values() if item.is_vegetarian]
