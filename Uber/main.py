import threading
from src.model.user import Rider, Driver
from src.model.location import Location
from src.model.product import UberGo, UberXL, ProductType
from src.service.ride_service import RideService
from src.service.fare_estimation_service import FareEstimationService
from src.service.eta_estimation_service import ETAEstimationService
from src.service.driver_matching_service import DriverMatchingService
from src.strategy.matching.driver_matching_strategy import NearestLocationStrategy, RatingBasedMatchingStrategy
from src.model.vehicle import Vehicle
from src.service.user_service import UserService
from src.common.exceptions import QuoteExpiredException
from datetime import timedelta

def simulate_ride_request(rider, pickup, dropoff, product, ride_service, force_expiry=False):
    print(f"[INFO]  Simulation : Rider {rider.name} requesting estimate for {product.product_type}...")
    quote = ride_service.get_estimate(pickup, dropoff, product)
    print(f"[DEBUG] Simulation : Quote generated: {quote.amount:.2f} (ID: {quote.quote_id})")
    
    if force_expiry:
        print(f"[WARN]  Simulation : Forcing expiry for Rider {rider.name}...")
        quote.expiry_time = quote.timestamp - timedelta(minutes=1) # Force expiry
        
    try:
        trip = ride_service.request_ride(rider, quote)
    except QuoteExpiredException as e:
        print(f"[WARN]  Client     : Quote expired. Refreshing...")
        quote = ride_service.get_estimate(pickup, dropoff, product)
        print(f"[INFO]  Client     : New Quote received: {quote.amount:.2f}")
        trip = ride_service.request_ride(rider, quote)
    
    if not trip:
         print(f"[ERROR] Simulation : Rider {rider.name} booking failed (System Error).")
         return

    if trip.driver:
        print(f"[INFO]  Client     : Rider {rider.name} matched with {trip.driver.name}. Fare: {trip.estimated_fare:.2f}")
        
        # Verify OTP and Start Ride
        print(f"[INFO]  Client     : Rider {rider.name} providing OTP {trip.otp}...")
        if ride_service.start_ride(trip.trip_id, trip.otp):
             # Simulate Ride
             pass
             # time.sleep(1) 
             ride_service.end_ride(trip.trip_id)
        else:
             print(f"[ERROR] Client     : Rider {rider.name} failed to start ride.")
             
    else:
        print(f"[WARN]  Simulation : Rider {rider.name} could not find a driver (No Match).")



# Already imported at top
# from src.services.user_service import UserService

def main():
    # 1. Setup Services
    user_svc = UserService()
    matching_strategy = NearestLocationStrategy()
    # matching_strategy = RatingBasedMatchingStrategy() # Swap to test rating logic
    # ENABLE SPATIAL INDEXING HERE (Toggle True/False)
    matching_svc = DriverMatchingService(matching_strategy, use_spatial_index=True)
    fare_svc = FareEstimationService()
    eta_svc = ETAEstimationService()
    ride_svc = RideService(fare_svc, eta_svc, matching_svc)

    # 2. Setup Drivers
    # Location(0,0) is center.
    v1 = Vehicle("Swift Dzire", "KA01AB1234", [ProductType.UBER_GO])
    v2 = Vehicle("Tata Tiago", "KA02CD5678", [ProductType.UBER_GO])
    v3 = Vehicle("Toyota Innova", "KA05XY9999", [ProductType.UBER_XL, ProductType.UBER_SHARE]) # Multi-product support

    d1 = Driver(101, "DriverA", "111", Location(0, 0), v1, rating=4.8)
    d2 = Driver(102, "DriverB", "222", Location(1, 1), v2, rating=4.9) # Higher rating but further
    d3 = Driver(103, "DriverC", "333", Location(10, 10), v3, rating=4.5)

    matching_svc.add_driver(d1)
    matching_svc.add_driver(d2)
    matching_svc.add_driver(d3)

    # 3. Setup Riders
    riders = [
        Rider(201, "Rider1", "999"),
        Rider(202, "Rider2", "888"),
        Rider(203, "Rider3", "777"),
        Rider(204, "Rider4", "666"), 
        Rider(205, "Rider5", "555"), # For TTL test
    ]
    
    for r in riders:
        user_svc.add_rider(r)

    # 4. Simulation: Concurrent Requests
    threads = []
    
    # Rider 1 -> UberGo
    t1 = threading.Thread(target=simulate_ride_request, args=(riders[0], Location(0,0), Location(5,5), UberGo(1), ride_svc))
    threads.append(t1)

    # Rider 2 -> UberGo (Competing for d1/d2)
    t2 = threading.Thread(target=simulate_ride_request, args=(user_svc.get_rider(202), Location(0.1,0.1), Location(6,6), UberGo(2), ride_svc))
    threads.append(t2)

    # Rider 4 -> UberGo (Competing)
    t4 = threading.Thread(target=simulate_ride_request, args=(user_svc.get_rider(204), Location(0.2,0.2), Location(7,7), UberGo(4), ride_svc))
    threads.append(t4)
    
    # Rider 3 -> UberXL (Should get d3)
    t3 = threading.Thread(target=simulate_ride_request, args=(user_svc.get_rider(203), Location(0,0), Location(5,5), UberXL(3), ride_svc))
    threads.append(t3)
    
    # Rider 5 -> TTL Test (Force Expiry)
    t5 = threading.Thread(target=simulate_ride_request, args=(user_svc.get_rider(205), Location(0,0), Location(5,5), UberGo(5), ride_svc, True))
    threads.append(t5)


    print("--- Starting Simulation ---")
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
    print("--- Simulation Ended ---")

if __name__ == "__main__":
    main()
