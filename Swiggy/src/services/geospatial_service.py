"""Geospatial service for distance calculations and location-based queries"""
import math
from typing import Tuple


class GeospatialService:
    """Service for geospatial operations"""
    
    EARTH_RADIUS_KM = 6371.0  # Earth's radius in kilometers
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon1_rad = math.radians(lon1)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        
        distance = self.EARTH_RADIUS_KM * c
        return distance
    
    def estimate_delivery_time(self, distance_km: float, 
                               preparation_time_minutes: int = 30) -> int:
        """
        Estimate total delivery time in minutes
        Assumes average speed of 20 km/h for delivery
        """
        avg_speed_kmh = 20.0
        travel_time_minutes = (distance_km / avg_speed_kmh) * 60
        total_time = preparation_time_minutes + travel_time_minutes
        return int(total_time)
    
    def is_within_delivery_radius(self, restaurant_lat: float, restaurant_lon: float,
                                   customer_lat: float, customer_lon: float,
                                   max_radius_km: float = 10.0) -> bool:
        """Check if customer is within delivery radius of restaurant"""
        distance = self.calculate_distance(
            restaurant_lat, restaurant_lon,
            customer_lat, customer_lon
        )
        return distance <= max_radius_km
