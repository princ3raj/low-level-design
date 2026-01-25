from typing import Dict
from src.model.user import Rider, Driver

class UserService:
    def __init__(self):
        self._riders: Dict[int, Rider] = {}
        self._drivers: Dict[int, Driver] = {}

    def add_rider(self, rider: Rider):
        self._riders[rider.user_id] = rider

    def add_driver(self, driver: Driver):
        self._drivers[driver.user_id] = driver

    def get_rider(self, user_id: int):
        return self._riders.get(user_id)

    def get_driver(self, user_id: int):
        return self._drivers.get(user_id)
