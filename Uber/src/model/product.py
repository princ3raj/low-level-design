from enum import Enum
from abc import ABC, abstractmethod

class ProductType(Enum):
    UBER_GO = "UberGo"
    UBER_XL = "UberXL"
    UBER_SHARE = "UberShare"

class Product(ABC):
    def __init__(self, id: int, name: str, product_type: ProductType):
        self.id = id
        self.name = name
        self.product_type = product_type

    @abstractmethod
    def get_base_rate(self):
        pass

    @abstractmethod
    def get_per_km_rate(self):
        pass

    @abstractmethod
    def get_per_min_rate(self):
        pass

class UberGo(Product):
    def __init__(self, id):
        super().__init__(id, "UberGo", ProductType.UBER_GO)
    
    def get_base_rate(self):
        return 50.0
    
    def get_per_km_rate(self):
        return 10.0
    
    def get_per_min_rate(self):
        return 2.0

class UberXL(Product):
    def __init__(self, id):
        super().__init__(id, "UberXL", ProductType.UBER_XL)
    
    def get_base_rate(self):
        return 80.0
    
    def get_per_km_rate(self):
        return 15.0
    
    def get_per_min_rate(self):
        return 3.0
