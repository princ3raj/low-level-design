"""Domain enums for the parking lot system."""
from enum import Enum


class VehicleType(str, Enum):
    """Types of vehicles that can use the parking lot."""
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    TRUCK = "TRUCK"
    VAN = "VAN"
    ELECTRIC_CAR = "ELECTRIC_CAR"


class SpotType(str, Enum):
    """Types of parking spots available."""
    COMPACT = "COMPACT"
    LARGE = "LARGE"
    HANDICAPPED = "HANDICAPPED"
    MOTORCYCLE = "MOTORCYCLE"
    ELECTRIC = "ELECTRIC"


class SpotStatus(str, Enum):
    """Status of a parking spot."""
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class TicketStatus(str, Enum):
    """Status of a parking ticket."""
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    LOST = "LOST"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    """Payment methods supported."""
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    WALLET = "WALLET"


class PaymentStatus(str, Enum):
    """Status of a payment."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class ReservationType(str, Enum):
    """Types of reservations."""
    HOURLY = "HOURLY"
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"


class ReservationStatus(str, Enum):
    """Status of a reservation."""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DiscountType(str, Enum):
    """Types of discounts."""
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
