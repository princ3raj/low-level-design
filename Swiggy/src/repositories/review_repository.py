"""Review repository"""
from typing import List
from .base_repository import BaseRepository
from ..domain.models.review import Review


class ReviewRepository(BaseRepository[Review]):
    """Repository for review entities"""
    
    def _get_entity_id(self, entity: Review) -> str:
        return entity.id
    
    def find_by_restaurant(self, restaurant_id: str) -> List[Review]:
        """Find all reviews for a restaurant"""
        reviews = [
            r for r in self._storage.values()
            if r.restaurant_id == restaurant_id
        ]
        reviews.sort(key=lambda r: r.created_at, reverse=True)
        return reviews
    
    def find_by_delivery_partner(self, partner_id: str) -> List[Review]:
        """Find all reviews for a delivery partner"""
        reviews = [
            r for r in self._storage.values()
            if r.delivery_partner_id == partner_id
        ]
        reviews.sort(key=lambda r: r.created_at, reverse=True)
        return reviews
    
    def find_by_customer(self, customer_id: str) -> List[Review]:
        """Find all reviews created by a customer"""
        reviews = [
            r for r in self._storage.values()
            if r.customer_id == customer_id
        ]
        reviews.sort(key=lambda r: r.created_at, reverse=True)
        return reviews
    
    def find_by_order(self, order_id: str) -> List[Review]:
        """Find all reviews for an order"""
        return [
            r for r in self._storage.values()
            if r.order_id == order_id
        ]
    
    def find_verified_reviews(self, restaurant_id: str) -> List[Review]:
        """Find verified reviews for a restaurant"""
        return [
            r for r in self._storage.values()
            if r.restaurant_id == restaurant_id and r.is_verified
        ]
    
    def calculate_average_rating(self, restaurant_id: str) -> float:
        """Calculate average rating for a restaurant"""
        reviews = self.find_by_restaurant(restaurant_id)
        if not reviews:
            return 5.0
        
        total_rating = sum(r.rating.value for r in reviews)
        return total_rating / len(reviews)
