from enum import Enum
from typing import Set, Dict


class OrderStatus(Enum):
    """Order status with state machine transitions"""
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    
    @staticmethod
    def get_allowed_transitions() -> Dict[str, Set[str]]:
        """Define allowed state transitions for order lifecycle"""
        return {
            OrderStatus.CREATED.value: {
                OrderStatus.CONFIRMED.value,
                OrderStatus.CANCELLED.value
            },
            OrderStatus.CONFIRMED.value: {
                OrderStatus.PREPARING.value,
                OrderStatus.CANCELLED.value
            },
            OrderStatus.PREPARING.value: {
                OrderStatus.READY.value
            },
            OrderStatus.READY.value: {
                OrderStatus.PICKED_UP.value
            },
            OrderStatus.PICKED_UP.value: {
                OrderStatus.DELIVERED.value
            },
            OrderStatus.DELIVERED.value: set(),  # Terminal state
            OrderStatus.CANCELLED.value: set()   # Terminal state
        }
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        """Check if transition from current status to new status is allowed"""
        allowed = self.get_allowed_transitions()
        return new_status.value in allowed.get(self.value, set())


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(Enum):
    """Payment method types"""
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    WALLET = "WALLET"


class DeliveryStatus(Enum):
    """Delivery tracking status"""
    ASSIGNED = "ASSIGNED"
    EN_ROUTE_TO_RESTAURANT = "EN_ROUTE_TO_RESTAURANT"
    AT_RESTAURANT = "AT_RESTAURANT"
    PICKED_UP = "PICKED_UP"
    EN_ROUTE_TO_CUSTOMER = "EN_ROUTE_TO_CUSTOMER"
    DELIVERED = "DELIVERED"
