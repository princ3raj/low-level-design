from datetime import datetime
from src.model.fare_quote import FareQuote
from src.strategy.pricing.pricing_strategy import  PricingStrategy, NightBasedPriceStrategy, LocationBasedPriceStrategy

class PricingStrategyFactory:
    @staticmethod
    def get_strategy():
        if FareEstimationService.is_night(): 
            return NightBasedPriceStrategy()
        return LocationBasedPriceStrategy()

class FareEstimationService:
    
    @staticmethod
    def is_night():
        current_hour = datetime.now().hour
        return current_hour < 6 or current_hour >= 22

    def calculate_fare_quote(self, pickup, dropoff, product) -> FareQuote:
        pricing_strategy = PricingStrategyFactory.get_strategy()
        distance = ((pickup.latitude - dropoff.latitude)**2 + (pickup.longitude - dropoff.longitude)**2)**0.5
        price = pricing_strategy.get_price(distance, product)
        
        return FareQuote(price, product, pickup, dropoff)
