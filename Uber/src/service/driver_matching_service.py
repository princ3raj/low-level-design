from typing import List
from threading import RLock
from src.model.user import Driver
from src.model.product import Product
from src.model.location import Location
from src.strategy.matching.driver_matching_strategy import DriverMatchingStrategy
from src.repository.driver_repository import DriverStorage, InMemoryListStorage, SpatialGridStorage

class DriverMatchingService:
    def __init__(self, strategy: DriverMatchingStrategy, use_spatial_index: bool = False):
        self._strategy = strategy
        self._use_spatial_index = use_spatial_index
        
        if use_spatial_index:
            self._storage: DriverStorage = SpatialGridStorage()
        else:
            self._storage: DriverStorage = InMemoryListStorage()

    def add_driver(self, driver: Driver):
        self._storage.add(driver)
        
    def find_nearest_driver(self, pickup: Location, product: Product) -> Driver:
        # 1. Efficient Lookup (O(K) or O(N))
        nearby_drivers = self._storage.get_nearby_drivers(pickup)
        
        # 2. Filter by Product
        candidate_drivers = [
            d for d in nearby_drivers 
            if d.vehicle.supports(product.product_type)
        ]
        
        # 3. Apply Matching Strategy
        return self._strategy.find_driver(pickup, candidate_drivers)
