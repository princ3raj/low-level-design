from threading import Lock
from enum import Enum
from src.model.location import Location
from src.model.vehicle import Vehicle

class UserType(Enum):
    RIDER = 1
    DRIVER = 2

class User:
    def __init__(self, user_id:int, name:str, phone:str, user_type:UserType):
        self._user_id = user_id
        self.name = name
        self.phone = phone
        self.user_type = user_type

    @property
    def user_id(self):
        """Getter for user_id"""
        return self._user_id

class Driver(User):

    def __init__(self, user_id, name, phone, location:Location, vehicle: Vehicle, rating: float = 5.0):
        super().__init__(user_id, name, phone, UserType.DRIVER)
        self.rating = rating
        self.location = location
        self.vehicle = vehicle
        self._is_available = True
        self._lock = Lock()
    
    def is_available(self):
        with self._lock:
            return self._is_available
            
    def mark_available(self):
        with self._lock:
            self._is_available = True

    def try_book(self) -> bool:
        """
        Atomically tries to book the driver.
        Returns True if successful (was available), False otherwise.
        """
        with self._lock:
            if self._is_available:
                self._is_available = False
                return True
            return False

class Rider(User):
    
    def __init__(self, user_id, name, phone):
        super().__init__(user_id, name, phone, UserType.RIDER)
