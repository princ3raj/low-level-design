from abc import ABC, abstractmethod
from typing import List

from src.model.user import Driver

class DriverMatchingStrategy(ABC):
    @abstractmethod
    def find_driver(self, pickup, candidate_drivers: List[Driver]) -> Driver:
        pass

class NearestLocationStrategy(DriverMatchingStrategy):
    def find_driver(self, pickup, candidate_drivers: List[Driver]) -> Driver:
        if not candidate_drivers:
            return None
            
        def get_distance(driver):
            # Simple Euclidean distance
            return ((driver.location.latitude - pickup.latitude)**2 + 
                   (driver.location.longitude - pickup.longitude)**2)**0.5
                   
        return min(candidate_drivers, key=get_distance)

class RatingBasedMatchingStrategy(DriverMatchingStrategy):
    """
    Matches the driver with the highest rating. 
    If ratings are tied, picks the nearest one among them.
    """
    def find_driver(self, pickup, candidate_drivers: List[Driver]) -> Driver:
        if not candidate_drivers:
            return None
            
        # Sort by rating (descending), then by distance (ascending)
        # We need distance for tie-breaking
        def get_sort_key(driver):
            distance = ((driver.location.latitude - pickup.latitude)**2 + 
                       (driver.location.longitude - pickup.longitude)**2)**0.5
            # tuple sort: -rating (primary), distance (secondary)
            return (-driver.rating, distance)
            
        return min(candidate_drivers, key=get_sort_key)
