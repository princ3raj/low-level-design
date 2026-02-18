from enum import Enum


class UserRole(Enum):
    """User role types in the system"""
    CUSTOMER = "CUSTOMER"
    RESTAURANT_OWNER = "RESTAURANT_OWNER"
    DELIVERY_PARTNER = "DELIVERY_PARTNER"
    ADMIN = "ADMIN"


class VehicleType(Enum):
    """Delivery vehicle types"""
    BICYCLE = "BICYCLE"
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    SCOOTER = "SCOOTER"


class SubscriptionPlan(Enum):
    """Subscription plan types for unlimited delivery"""
    NONE = "NONE"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
