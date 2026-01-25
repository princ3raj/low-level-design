import random
from src.model.user import Driver
from src.model.location import Location
from src.model.product import Product
from src.model.trip import Trip, TripStatus
from src.model.fare_quote import FareQuote
from src.service.driver_matching_service import DriverMatchingService
from src.service.fare_estimation_service import FareEstimationService
from src.service.eta_estimation_service import ETAEstimationService
from src.common.exceptions import QuoteExpiredException

class RideService:
    """The Logic Layer/Service that orchestrates the workflow"""
    def __init__(self, fare_estimation_svc: FareEstimationService, eta_svc: ETAEstimationService, matching_svc: DriverMatchingService):
        self.fare_estimation_svc = fare_estimation_svc
        self.eta_svc = eta_svc
        self.matching_svc = matching_svc
        self._trips = {} # trip_id -> Trip

    def get_estimate(self, pickup: Location, dropoff: Location, product: Product) -> 'FareQuote':
        return self.fare_estimation_svc.calculate_fare_quote(pickup, dropoff, product)

    def request_ride(self, rider, quote: 'FareQuote'):
        if quote.is_expired():
            raise QuoteExpiredException(f"Quote {quote.quote_id} has expired.")
            
        pickup = quote.pickup
        dropoff = quote.dropoff
        product = quote.product
        
        new_trip = Trip(rider, pickup, dropoff, product)
        new_trip.estimated_fare = quote.amount # Use the locked price
        eta = self.eta_svc.get_eta(pickup, dropoff)
        
        # Try to find a driver with retries to handle concurrency
        MAX_RETRIES = 5
        for _ in range(MAX_RETRIES):
            driver: Driver = self.matching_svc.find_nearest_driver(pickup, product)
            if not driver:
                break # No drivers available at all
            
            if driver.try_book():
                new_trip.driver = driver
                new_trip.status = TripStatus.ASSIGNED
                new_trip.otp = random.randint(1000, 9999) # Generate 4-digit OTP
                self._trips[new_trip.trip_id] = new_trip
                
                print(f"[INFO]  RideService: Trip {new_trip.trip_id} assigned to Driver {driver.name}. OTP: {new_trip.otp}")
                return new_trip
                
        # If we reach here, no driver could be booked
        print(f"[WARN]  RideService: Failed to assign driver for Trip {new_trip.trip_id} after {MAX_RETRIES} retries")
        return new_trip

    def start_ride(self, trip_id: str, otp: int) -> bool:
        trip = self._trips.get(trip_id)
        if not trip:
            print(f"[ERROR] RideService: Trip {trip_id} not found.")
            return False
            
        # Delegate logic to the Rich Domain Model
        if trip.start_ride(otp):
             print(f"[INFO]  RideService: Trip {trip_id} STARTED. Rider {trip.rider.name} picked up by {trip.driver.name}.")
             return True
        
        print(f"[ERROR] RideService: Failed to start trip {trip_id} (Invalid OTP or State).")
        return False

    def end_ride(self, trip_id: str) -> bool:
        trip = self._trips.get(trip_id)
        if not trip:
            return False
        
        if trip.end_ride():
             print(f"[INFO]  RideService: Trip {trip_id} COMPLETED. Driver {trip.driver.name} is now available.")
             return True
             
        print(f"[ERROR] RideService: Failed to end trip {trip_id}.")
        return False
