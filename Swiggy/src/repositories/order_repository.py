"""Order repository with optimistic locking support"""
from typing import List, Optional
from datetime import datetime
from .base_repository import BaseRepository
from ..domain.models.order import Order, OrderItem
from ..domain.enums import OrderStatus


class OrderRepository(BaseRepository[Order]):
    """Repository for order entities with concurrency control"""
    
    def _get_entity_id(self, entity: Order) -> str:
        return entity.id
    
    def save_with_version_check(self, order: Order, expected_version: int) -> Order:
        """
        Save order with optimistic locking
        Raises ValueError if version mismatch (concurrent modification detected)
        """
        existing_order = self.find_by_id(order.id)
        
        if existing_order and existing_order.version != expected_version:
            raise ValueError(
                f"Concurrent modification detected for order {order.id}. "
                f"Expected version {expected_version}, found {existing_order.version}"
            )
        
        # Increment version
        order.version = expected_version + 1
        return self.save(order)
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        """Find all orders for a customer"""
        orders = [
            order for order in self._storage.values()
            if order.customer_id == customer_id
        ]
        # Sort by created_at descending (newest first)
        orders.sort(key=lambda o: o.created_at, reverse=True)
        return orders
    
    def find_by_restaurant(self, restaurant_id: str) -> List[Order]:
        """Find all orders for a restaurant"""
        orders = [
            order for order in self._storage.values()
            if order.restaurant_id == restaurant_id
        ]
        orders.sort(key=lambda o: o.created_at, reverse=True)
        return orders
    
    def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Find all orders with a specific status"""
        return [
            order for order in self._storage.values()
            if order.status == status
        ]
    
    def find_active_orders(self) -> List[Order]:
        """Find all non-terminal orders"""
        terminal_states = {OrderStatus.DELIVERED, OrderStatus.CANCELLED}
        return [
            order for order in self._storage.values()
            if order.status not in terminal_states
        ]
    
    def find_scheduled_orders(self) -> List[Order]:
        """Find orders scheduled for later delivery"""
        now = datetime.now()
        return [
            order for order in self._storage.values()
            if order.scheduled_for and order.scheduled_for > now
        ]
    
    def find_ready_scheduled_orders(self) -> List[Order]:
        """Find scheduled orders that are ready to be processed"""
        now = datetime.now()
        return [
            order for order in self._storage.values()
            if (order.scheduled_for and 
                order.scheduled_for <= now and 
                order.status == OrderStatus.CREATED)
        ]


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository for order items"""
    
    def _get_entity_id(self, entity: OrderItem) -> str:
        return entity.id
    
    def find_by_order(self, order_id: str) -> List[OrderItem]:
        """Find all items for an order"""
        return [
            item for item in self._storage.values()
            if item.order_id == order_id
        ]
