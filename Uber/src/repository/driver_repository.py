from abc import ABC, abstractmethod
from typing import List
from threading import RLock

from src.model.user import Driver
from src.model.location import Location
from src.common.spatial_index import SpatialIndex

class DriverStorage(ABC):
    @abstractmethod
    def add(self, driver: Driver):
        pass
        
    @abstractmethod
    def get_nearby_drivers(self, location: Location) -> List[Driver]:
        pass

class InMemoryListStorage(DriverStorage):
    """
    O(N) Complexity.
    Stores drivers in a simple list. Returns ALL drivers for 'nearby' queries 
    (relying on the strategy to filter by distance).
    """
    def __init__(self):
        self._drivers: List[Driver] = []
        self._lock = RLock()
        
    def add(self, driver: Driver):
         with self._lock:
            self._drivers.append(driver)
            
    def get_nearby_drivers(self, location: Location) -> List[Driver]:
        with self._lock:
            return list(self._drivers) # Return copy

class SpatialGridStorage(DriverStorage):
    """
    O(K) Complexity.
    Stores drivers in a Grid Spatial Index. Returns only drivers in 
    neighboring cells.
    """
    def __init__(self):
        self._index = SpatialIndex()
        self._lock = RLock()
        
    def add(self, driver: Driver):
        with self._lock:
            self._index.update(driver)
            
    def get_nearby_drivers(self, location: Location) -> List[Driver]:
        with self._lock:
            return self._index.search(location)
