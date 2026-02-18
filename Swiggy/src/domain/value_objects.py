"""Value objects for the domain layer"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Location:
    """Immutable location value object"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")
    
    def to_tuple(self) -> tuple:
        """Return (latitude, longitude) tuple for geospatial calculations"""
        return (self.latitude, self.longitude)


@dataclass(frozen=True)
class Money:
    """Immutable money value object"""
    amount: float
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, factor: float) -> 'Money':
        return Money(self.amount * factor, self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class Rating:
    """Immutable rating value object"""
    value: float
    
    def __post_init__(self):
        if not (0 <= self.value <= 5):
            raise ValueError("Rating must be between 0 and 5")
    
    def __str__(self) -> str:
        return f"{self.value:.1f}/5.0"
