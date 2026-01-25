from enum import Enum
import uuid
import random
from typing import List

from src.model.location import Location
from src.model.product import Product
from src.model.user import Rider, Driver

class TripStatus(Enum):
    REQUESTED = "REQUESTED"      
    ASSIGNED = "ASSIGNED"        
    IN_TRANSIT = "IN_TRANSIT"    
    COMPLETED = "COMPLETED"     
    CANCELLED = "CANCELLED" 

class Trip:
    """The Domain Object holding Trip data"""
    def __init__(self, rider: Rider, pickup: Location, dropoff: Location, product: Product):
        self.trip_id = str(uuid.uuid4())
        self.rider = rider
        self.driver = None
        self.pickup = pickup
        self.dropoff = dropoff
        self.product = product
        self.estimated_fare = 0.0
        self.status = TripStatus.REQUESTED
        self.otp = None

    def start_ride(self, otp: int) -> bool:
        """
        Domain method to handle state transition.
        """
        if self.status != TripStatus.ASSIGNED:
            # Could raise exception here too
            return False
            
        if self.otp != otp:
            return False
            
        self.status = TripStatus.IN_TRANSIT
        return True

    def end_ride(self):
        if self.status != TripStatus.IN_TRANSIT:
             return False
        self.status = TripStatus.COMPLETED
        if self.driver:
            self.driver.mark_available()
        return True
