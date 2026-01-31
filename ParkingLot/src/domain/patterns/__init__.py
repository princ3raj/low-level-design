"""Design patterns package."""
from src.domain.patterns.factory import SpotFactory
from src.domain.patterns.observer import (
    AvailabilityObserver,
    CacheInvalidationObserver,
    NotificationObserver,
    Observer,
    Subject,
)
from src.domain.patterns.singleton import ParkingLotManager
from src.domain.patterns.strategy import (
    DynamicPricingStrategy,
    EVChargingPricingStrategy,
    HourlyPricingStrategy,
    PricingStrategy,
    ReservedPricingStrategy,
    ValetPricingStrategy,
)

__all__ = [
    "SpotFactory",
    "PricingStrategy",
    "HourlyPricingStrategy",
    "DynamicPricingStrategy",
    "ReservedPricingStrategy",
    "ValetPricingStrategy",
    "EVChargingPricingStrategy",
    "Observer",
    "Subject",
    "AvailabilityObserver",
    "CacheInvalidationObserver",
    "NotificationObserver",
    "ParkingLotManager",
]
