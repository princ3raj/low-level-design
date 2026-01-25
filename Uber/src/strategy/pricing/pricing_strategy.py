from datetime import datetime
from abc import ABC, abstractmethod
from src.model.product import Product

class PricingStrategy(ABC):
    @abstractmethod
    def get_price(self, distance, product) -> float:
        pass

class NightBasedPriceStrategy(PricingStrategy):
    def get_price(self, distance, product):
        # Night rate: Base + (Dist * Rate) * NightMultiplier
        return (product.get_base_rate() + (distance * product.get_per_km_rate())) * 1.5

class LocationBasedPriceStrategy(PricingStrategy):
    def get_price(self, distance, product):
        return product.get_base_rate() + (distance * product.get_per_km_rate())
