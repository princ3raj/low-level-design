from src.model.location import Location
import random

class ETAEstimationService:
    def get_eta(self, pickup: Location, dropoff: Location) -> int:
        # Simulate call to Google Maps/Routing Engine
        # Returns seconds
        return random.randint(300, 1800) 
