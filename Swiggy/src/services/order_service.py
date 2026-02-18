"""Order service with state machine management"""
from typing import List, Optional, Dict
from datetime import datetime
from ..domain.models.order import Order, OrderItem
from ..domain.models.user import Customer
from ..domain.models.restaurant import Restaurant
from ..domain.enums import OrderStatus
from ..domain.value_objects import Money, Location
from ..domain.exceptions import (
    InvalidOrderStateTransition,
    InsufficientInventory,
    RestaurantNotActive
)
from ..repositories.order_repository import OrderRepository, OrderItemRepository
from ..repositories.restaurant_repository import RestaurantRepository
from ..repositories.user_repository import CustomerRepository


class OrderService:
    """Service for order lifecycle management"""
    
    def __init__(self,
                 order_repo: OrderRepository,
                 order_item_repo: OrderItemRepository,
                 restaurant_repo: RestaurantRepository,
                 customer_repo: CustomerRepository):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.restaurant_repo = restaurant_repo
        self.customer_repo = customer_repo
    
    def create_order(self, customer_id: str, restaurant_id: str,
                     items: List[Dict], delivery_address: Location,
                     scheduled_for: Optional[datetime] = None) -> Order:
        """
        Create a new order
        items: List of dicts with 'menu_item_id', 'quantity', 'special_instructions'
        """
        # Validate restaurant
        restaurant = self.restaurant_repo.find_by_id(restaurant_id)
        if not restaurant:
            raise ValueError(f"Restaurant {restaurant_id} not found")
        
        if not restaurant.is_accepting_orders():
            raise RestaurantNotActive(restaurant_id)
        
        # Get customer for subscription check
        customer = self.customer_repo.find_by_id(customer_id)
        is_subscription_order = customer.has_active_subscription() if customer else False
        
        # Create order
        order = Order(
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            delivery_address=delivery_address,
            delivery_fee=restaurant.delivery_fee,
            scheduled_for=scheduled_for,
            is_subscription_order=is_subscription_order
        )
        
        # Add items
        for item_data in items:
            menu_item = restaurant.get_menu_item(item_data['menu_item_id'])
            
            if not menu_item:
                raise ValueError(f"Menu item {item_data['menu_item_id']} not found")
            
            if not menu_item.is_available:
                raise InsufficientInventory(menu_item.name)
            
            order_item = OrderItem(
                menu_item_id=menu_item.id,
                menu_item_name=menu_item.name,
                quantity=item_data.get('quantity', 1),
                unit_price=menu_item.price,
                special_instructions=item_data.get('special_instructions', '')
            )
            
            order.add_item(order_item)
            self.order_item_repo.save(order_item)
        
        # Calculate loyalty points
        order.calculate_loyalty_points_earned()
        
        # Save order
        self.order_repo.save(order)
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.order_repo.find_by_id(order_id)
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get all orders for a customer"""
        return self.order_repo.find_by_customer(customer_id)
    
    def get_restaurant_orders(self, restaurant_id: str) -> List[Order]:
        """Get all orders for a restaurant"""
        return self.order_repo.find_by_restaurant(restaurant_id)
    
    def update_order_status(self, order_id: str, new_status: OrderStatus) -> Order:
        """
        Update order status with state machine validation
        """
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Use state machine to validate transition
        order.transition_to(new_status)
        
        # Award loyalty points when order is delivered
        if new_status == OrderStatus.DELIVERED and order.loyalty_points_earned > 0:
            customer = self.customer_repo.find_by_id(order.customer_id)
            if customer:
                customer.add_loyalty_points(order.loyalty_points_earned)
                self.customer_repo.save(customer)
        
        # Save with version increment
        self.order_repo.save_with_version_check(order, order.version)
        
        return order
    
    def cancel_order(self, order_id: str, reason: str) -> Order:
        """Cancel an order"""
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        order.cancel(reason)
        self.order_repo.save(order)
        
        return order
    
    def apply_loyalty_discount(self, order_id: str, points: int) -> Order:
        """Apply loyalty points discount to order"""
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if not order.can_be_modified():
            raise ValueError("Order can no longer be modified")
        
        customer = self.customer_repo.find_by_id(order.customer_id)
        if not customer:
            raise ValueError("Customer not found")
        
        if not customer.redeem_loyalty_points(points):
            raise ValueError("Insufficient loyalty points")
        
        order.apply_loyalty_points(points)
        self.order_repo.save(order)
        self.customer_repo.save(customer)
        
        return order
    
    def get_active_orders(self) -> List[Order]:
        """Get all active (non-terminal) orders"""
        return self.order_repo.find_active_orders()
    
    def process_scheduled_orders(self) -> List[Order]:
        """
        Process scheduled orders that are ready
        Returns list of orders that were processed
        """
        ready_orders = self.order_repo.find_ready_scheduled_orders()
        processed = []
        
        for order in ready_orders:
            try:
                self.update_order_status(order.id, OrderStatus.CONFIRMED)
                processed.append(order)
            except Exception as e:
                print(f"Failed to process scheduled order {order.id}: {e}")
        
        return processed
