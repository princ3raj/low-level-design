"""Order domain models with state machine"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..enums import OrderStatus
from ..value_objects import Money, Location
from ..exceptions import InvalidOrderStateTransition, OrderAlreadyCancelled


@dataclass
class OrderItem:
    """Order item entity"""
    id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    menu_item_id: str = ""
    menu_item_name: str = ""
    quantity: int = 1
    unit_price: Money = field(default_factory=lambda: Money(0.0))
    special_instructions: str = ""
    
    @property
    def total_price(self) -> Money:
        """Calculate total price for this item"""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Order entity with state machine"""
    id: str = field(default_factory=lambda: str(uuid4()))
    customer_id: str = ""
    restaurant_id: str = ""
    items: List[OrderItem] = field(default_factory=list)
    delivery_address: Optional[Location] = None
    status: OrderStatus = OrderStatus.CREATED
    subtotal: Money = field(default_factory=lambda: Money(0.0))
    delivery_fee: Money = field(default_factory=lambda: Money(40.0))
    discount: Money = field(default_factory=lambda: Money(0.0))
    tax: Money = field(default_factory=lambda: Money(0.0))
    total: Money = field(default_factory=lambda: Money(0.0))
    created_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    scheduled_for: Optional[datetime] = None  # For scheduled orders
    is_subscription_order: bool = False  # Free delivery for subscribers
    loyalty_points_used: int = 0
    loyalty_points_earned: int = 0
    version: int = 0  # For optimistic locking
    
    def add_item(self, item: OrderItem):
        """Add item to order"""
        item.order_id = self.id
        self.items.append(item)
        self._recalculate_totals()
    
    def remove_item(self, item_id: str):
        """Remove item from order"""
        self.items = [item for item in self.items if item.id != item_id]
        self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = Money(
            sum(item.total_price.amount for item in self.items)
        )
        
        # Apply free delivery for subscription orders
        actual_delivery_fee = Money(0.0) if self.is_subscription_order else self.delivery_fee
        
        # Calculate tax (example: 5% GST)
        tax_amount = self.subtotal.amount * 0.05
        self.tax = Money(tax_amount)
        
        # Total = Subtotal + Delivery + Tax - Discount
        self.total = self.subtotal + actual_delivery_fee + self.tax - self.discount
    
    def apply_discount(self, discount: Money):
        """Apply discount to order"""
        self.discount = discount
        self._recalculate_totals()
    
    def apply_loyalty_points(self, points: int, conversion_rate: float = 0.1):
        """Apply loyalty points as discount (example: 1 point = 0.1 INR)"""
        discount_amount = points * conversion_rate
        self.loyalty_points_used = points
        self.discount = self.discount + Money(discount_amount)
        self._recalculate_totals()
    
    def calculate_loyalty_points_earned(self, earning_rate: float = 0.01):
        """Calculate loyalty points to be earned (example: 1% of total)"""
        self.loyalty_points_earned = int(self.total.amount * earning_rate)
    
    def transition_to(self, new_status: OrderStatus):
        """
        Transition order to new status with validation
        Implements state machine pattern
        """
        if self.status == OrderStatus.CANCELLED:
            raise OrderAlreadyCancelled(self.id)
        
        if not self.status.can_transition_to(new_status):
            raise InvalidOrderStateTransition(
                self.status.value,
                new_status.value
            )
        
        self.status = new_status
        
        # Update timestamps based on status
        if new_status == OrderStatus.CONFIRMED:
            self.confirmed_at = datetime.now()
        elif new_status == OrderStatus.DELIVERED:
            self.delivered_at = datetime.now()
        elif new_status == OrderStatus.CANCELLED:
            self.cancelled_at = datetime.now()
    
    def cancel(self, reason: str):
        """Cancel the order"""
        if self.status == OrderStatus.CANCELLED:
            raise OrderAlreadyCancelled(self.id)
        
        # Can only cancel from CREATED or CONFIRMED states
        if self.status not in [OrderStatus.CREATED, OrderStatus.CONFIRMED]:
            raise InvalidOrderStateTransition(
                self.status.value,
                OrderStatus.CANCELLED.value
            )
        
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.cancellation_reason = reason
    
    def is_scheduled(self) -> bool:
        """Check if this is a scheduled order for later delivery"""
        return self.scheduled_for is not None and self.scheduled_for > datetime.now()
    
    def can_be_modified(self) -> bool:
        """Check if order can still be modified"""
        return self.status in [OrderStatus.CREATED, OrderStatus.CONFIRMED]
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.CREATED, OrderStatus.CONFIRMED]
