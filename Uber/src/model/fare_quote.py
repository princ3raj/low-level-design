from datetime import datetime, timedelta
import uuid
from src.model.location import Location
from src.model.product import Product

class FareQuote:
    def __init__(self, amount: float, product: Product, pickup: Location, dropoff: Location):
        self.quote_id = str(uuid.uuid4())
        self.amount = amount
        self.product = product
        self.pickup = pickup
        self.dropoff = dropoff
        self.timestamp = datetime.now()
        self.ttl_minutes = 5
        self.expiry_time = self.timestamp + timedelta(minutes=self.ttl_minutes)

    def is_expired(self) -> bool:
        return datetime.now() > self.expiry_time
