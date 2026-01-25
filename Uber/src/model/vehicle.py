from typing import List
from src.model.product import ProductType

class Vehicle:
    def __init__(self, model: str, plate: str, supported_products: List[ProductType]):
        self.model = model
        self.plate = plate
        self.supported_products = supported_products
        
    def supports(self, product_type: ProductType) -> bool:
        return product_type in self.supported_products
