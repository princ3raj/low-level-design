"""Review and rating service"""
from typing import List, Optional
from ..domain.models.review import Review
from ..domain.value_objects import Rating
from ..repositories.review_repository import ReviewRepository
from ..repositories.restaurant_repository import RestaurantRepository
from ..repositories.user_repository import DeliveryPartnerRepository
from ..repositories.order_repository import OrderRepository


class ReviewService:
    """Service for managing reviews and ratings"""
    
    def __init__(self,
                 review_repo: ReviewRepository,
                 restaurant_repo: RestaurantRepository,
                 partner_repo: DeliveryPartnerRepository,
                 order_repo: OrderRepository):
        self.review_repo = review_repo
        self.restaurant_repo = restaurant_repo
        self.partner_repo = partner_repo
        self.order_repo = order_repo
    
    def create_restaurant_review(self, customer_id: str, order_id: str,
                                 restaurant_id: str, rating: float,
                                 comment: str = "") -> Review:
        """Create a review for a restaurant"""
        # Verify customer actually ordered from this restaurant
        order = self.order_repo.find_by_id(order_id)
        is_verified = (order and 
                      order.customer_id == customer_id and
                      order.restaurant_id == restaurant_id)
        
        review = Review(
            customer_id=customer_id,
            order_id=order_id,
            restaurant_id=restaurant_id,
            rating=Rating(rating),
            comment=comment,
            is_verified=is_verified
        )
        
        self.review_repo.save(review)
        
        # Update restaurant rating
        self._update_restaurant_rating(restaurant_id)
        
        return review
    
    def create_delivery_review(self, customer_id: str, order_id: str,
                               delivery_partner_id: str, rating: float,
                               comment: str = "") -> Review:
        """Create a review for a delivery partner"""
        # Verify delivery
        order = self.order_repo.find_by_id(order_id)
        is_verified = order and order.customer_id == customer_id
        
        review = Review(
            customer_id=customer_id,
            order_id=order_id,
            delivery_partner_id=delivery_partner_id,
            rating=Rating(rating),
            comment=comment,
            is_verified=is_verified
        )
        
        self.review_repo.save(review)
        
        # Update partner rating
        self._update_partner_rating(delivery_partner_id)
        
        return review
    
    def get_restaurant_reviews(self, restaurant_id: str) -> List[Review]:
        """Get all reviews for a restaurant"""
        return self.review_repo.find_by_restaurant(restaurant_id)
    
    def get_delivery_partner_reviews(self, partner_id: str) -> List[Review]:
        """Get all reviews for a delivery partner"""
        return self.review_repo.find_by_delivery_partner(partner_id)
    
    def _update_restaurant_rating(self, restaurant_id: str):
        """Update restaurant's average rating"""
        restaurant = self.restaurant_repo.find_by_id(restaurant_id)
        if not restaurant:
            return
        
        avg_rating = self.review_repo.calculate_average_rating(restaurant_id)
        restaurant.update_rating(avg_rating)
        self.restaurant_repo.save(restaurant)
    
    def _update_partner_rating(self, partner_id: str):
        """Update delivery partner's average rating"""
        partner = self.partner_repo.find_by_id(partner_id)
        if not partner:
            return
        
        reviews = self.review_repo.find_by_delivery_partner(partner_id)
        if not reviews:
            return
        
        avg_rating = sum(r.rating.value for r in reviews) / len(reviews)
        partner.update_rating(avg_rating)
        self.partner_repo.save(partner)
