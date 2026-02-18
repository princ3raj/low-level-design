"""Custom domain exceptions for the food delivery platform"""


class DomainException(Exception):
    """Base exception for all domain-level errors"""
    pass


class InvalidOrderStateTransition(DomainException):
    """Raised when attempting an invalid order status transition"""
    
    def __init__(self, current_status: str, new_status: str):
        self.current_status = current_status
        self.new_status = new_status
        super().__init__(
            f"Cannot transition order from {current_status} to {new_status}"
        )


class InsufficientInventory(DomainException):
    """Raised when menu item is not available or out of stock"""
    
    def __init__(self, item_name: str):
        self.item_name = item_name
        super().__init__(f"Item '{item_name}' is not available")


class NoDeliveryPartnerAvailable(DomainException):
    """Raised when no delivery partner can be assigned"""
    
    def __init__(self, reason: str = "No available delivery partners"):
        super().__init__(reason)


class RestaurantNotActive(DomainException):
    """Raised when attempting to order from inactive restaurant"""
    
    def __init__(self, restaurant_id: str):
        super().__init__(f"Restaurant {restaurant_id} is not accepting orders")


class OrderAlreadyCancelled(DomainException):
    """Raised when attempting to modify a cancelled order"""
    
    def __init__(self, order_id: str):
        super().__init__(f"Order {order_id} has already been cancelled")


class PaymentFailed(DomainException):
    """Raised when payment processing fails"""
    
    def __init__(self, reason: str):
        super().__init__(f"Payment failed: {reason}")


class InvalidLocation(DomainException):
    """Raised when location coordinates are invalid"""
    
    def __init__(self, latitude: float, longitude: float):
        super().__init__(
            f"Invalid location coordinates: ({latitude}, {longitude})"
        )


class UnauthorizedAccess(DomainException):
    """Raised when user attempts unauthorized action"""
    
    def __init__(self, user_id: str, action: str):
        super().__init__(
            f"User {user_id} is not authorized to perform {action}"
        )
