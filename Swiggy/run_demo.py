"""
Food Delivery Platform - Comprehensive Demo Script
Demonstrates all core features and extension scenarios
"""

from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.domain.models.user import Customer, DeliveryPartner, RestaurantOwner
from src.domain.models.restaurant import Restaurant, MenuCategory, MenuItem
from src.domain.value_objects import Location, Money, Rating
from src.domain.enums import OrderStatus, SubscriptionPlan, VehicleType
from src.repositories.user_repository import (
    CustomerRepository, DeliveryPartnerRepository, RestaurantOwnerRepository
)
from src.repositories.restaurant_repository import RestaurantRepository, MenuCategoryRepository, MenuItemRepository
from src.repositories.order_repository import OrderRepository, OrderItemRepository
from src.repositories.delivery_repository import DeliveryRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.review_repository import ReviewRepository
from src.services.restaurant_service import RestaurantService
from src.services.order_service import OrderService
from src.services.delivery_assignment_service import (
    DeliveryAssignmentService, NearestPartnerStrategy
)
from src.services.payment_service import PaymentService
from src.services.review_service import ReviewService
from src.services.geospatial_service import GeospatialService


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    """Run the comprehensive demo"""
    
    print_section("FOOD DELIVERY PLATFORM - DEMO")
    print("Production-grade Low-Level Design Implementation")
    print("Features: State Machine, Repository Pattern, Strategy Pattern,")
    print("         Factory Pattern, Geospatial Queries, Optimistic Locking\n")
    
    # Initialize repositories
    customer_repo = CustomerRepository()
    partner_repo = DeliveryPartnerRepository()
    owner_repo = RestaurantOwnerRepository()
    restaurant_repo = RestaurantRepository()
    category_repo = MenuCategoryRepository()
    item_repo = MenuItemRepository()
    order_repo = OrderRepository()
    order_item_repo = OrderItemRepository()
    delivery_repo = DeliveryRepository()
    payment_repo = PaymentRepository()
    review_repo = ReviewRepository()
    
    # Initialize services
    geo_service = GeospatialService()
    restaurant_service = RestaurantService(restaurant_repo, category_repo, item_repo)
    order_service = OrderService(order_repo, order_item_repo, restaurant_repo, customer_repo)
    delivery_service = DeliveryAssignmentService(
        partner_repo, delivery_repo, order_repo, geo_service,
        NearestPartnerStrategy(geo_service)
    )
    payment_service = PaymentService(payment_repo)
    review_service = ReviewService(review_repo, restaurant_repo, partner_repo, order_repo)
    
    # =========================
    # 1. CREATE USERS
    # =========================
    print_section("1. Creating Users")
    
    # Create customers
    customer1 = Customer(
        name="Alice Johnson",
        email="alice@example.com",
        phone="+91-9876543210",
        loyalty_points=100,
        subscription_plan=SubscriptionPlan.MONTHLY,
        subscription_expiry=datetime.now() + timedelta(days=30)
    )
    customer1.addresses.append(Location(
        latitude=12.9716,
        longitude=77.5946,
        address="123 MG Road, Bangalore",
        city="Bangalore"
    ))
    customer_repo.save(customer1)
    print(f"✓ Created Customer: {customer1.name} (Subscription: {customer1.subscription_plan.value})")
    
    customer2 = Customer(
        name="Bob Smith",
        email="bob@example.com",
        phone="+91-9876543211",
        loyalty_points=50
    )
    customer2.addresses.append(Location(
        latitude=12.9350,
        longitude=77.6206,
        address="456 Indiranagar, Bangalore"
    ))
    customer_repo.save(customer2)
    print(f"✓ Created Customer: {customer2.name} (Loyalty Points: {customer2.loyalty_points})")
    
    # Create restaurant owners
    owner1 = RestaurantOwner(
        name="Chef Ramesh",
        email="ramesh@restaurant.com",
        phone="+91-9876543212"
    )
    owner_repo.save(owner1)
    print(f"✓ Created Restaurant Owner: {owner1.name}")
    
    # Create delivery partners
    partner1 = DeliveryPartner(
        name="Rajesh Kumar",
        email="rajesh@delivery.com",
        phone="+91-9876543213",
        vehicle_type=VehicleType.MOTORCYCLE,
        current_location=Location(latitude=12.9716, longitude=77.5946)
    )
    partner_repo.save(partner1)
    print(f"✓ Created Delivery Partner: {partner1.name} ({partner1.vehicle_type.value})")
    
    partner2 = DeliveryPartner(
        name="Suresh Patel",
        email="suresh@delivery.com",
        phone="+91-9876543214",
        vehicle_type=VehicleType.BICYCLE,
        current_location=Location(latitude=12.9350, longitude=77.6206)
    )
    partner_repo.save(partner2)
    print(f"✓ Created Delivery Partner: {partner2.name} ({partner2.vehicle_type.value})")
    
    # =========================
    # 2. CREATE RESTAURANTS
    # =========================
    print_section("2. Creating Restaurants with Menus")
    
    # Restaurant 1: South Indian
    restaurant1 = restaurant_service.create_restaurant(
        owner_id=owner1.id,
        name="Spice Paradise",
        location=Location(
            latitude=12.9750,
            longitude=77.6050,
            address="100 Brigade Road, Bangalore"
        ),
        cuisine_types=["South Indian", "North Indian"],
        description="Authentic Indian cuisine"
    )
    print(f"✓ Created Restaurant: {restaurant1.name}")
    
    # Add menu categories and items
    category1 = restaurant_service.add_menu_category(
        restaurant1.id,
        "Main Course",
        "Delicious main dishes"
    )
    
    item1 = restaurant_service.add_menu_item(
        category1.id,
        "Masala Dosa",
        Money(150.0),
        description="Crispy dosa with potato filling",
        is_vegetarian=True,
        preparation_time_minutes=15
    )
    print(f"  └─ Added: {item1.name} - ₹{item1.price.amount}")
    
    item2 = restaurant_service.add_menu_item(
        category1.id,
        "Chicken Biryani",
        Money(300.0),
        description="Aromatic basmati rice with chicken",
        is_vegetarian=False,
        preparation_time_minutes=25
    )
    print(f"  └─ Added: {item2.name} - ₹{item2.price.amount}")
    
    category2 = restaurant_service.add_menu_category(
        restaurant1.id,
        "Beverages",
        "Refreshing drinks"
    )
    
    item3 = restaurant_service.add_menu_item(
        category2.id,
        "Fresh Lime Soda",
        Money(50.0),
        description="Chilled lime soda",
        is_vegetarian=True,
        preparation_time_minutes=5
    )
    print(f"  └─ Added: {item3.name} - ₹{item3.price.amount}")
    
    # Restaurant 2: Chinese
    restaurant2 = restaurant_service.create_restaurant(
        owner_id=owner1.id,
        name="Dragon Wok",
        location=Location(
            latitude=12.9300,
            longitude=77.6200,
            address="200 Koramangala, Bangalore"
        ),
        cuisine_types=["Chinese", "Asian"],
        description="Authentic Chinese food"
    )
    print(f"\n✓ Created Restaurant: {restaurant2.name}")
    
    category3 = restaurant_service.add_menu_category(
        restaurant2.id,
        "Noodles & Rice",
        "Asian favorites"
    )
    
    item4 = restaurant_service.add_menu_item(
        category3.id,
        "Hakka Noodles",
        Money(180.0),
        description="Spicy noodles with vegetables",
        is_vegetarian=True,
        preparation_time_minutes=20
    )
    print(f"  └─ Added: {item4.name} - ₹{item4.price.amount}")
    
    # =========================
    # 3. BROWSE NEARBY RESTAURANTS
    # =========================
    print_section("3. Customer Browsing Nearby Restaurants")
    
    customer_location = customer1.addresses[0]
    print(f"Customer location: {customer_location.address}")
    
    nearby = restaurant_service.get_nearby_restaurants(
        customer_location.latitude,
        customer_location.longitude,
        radius_km=5.0
    )
    
    print(f"\nFound {len(nearby)} restaurants within 5 km:")
    for restaurant in nearby:
        distance = geo_service.calculate_distance(
            customer_location.latitude,
            customer_location.longitude,
            restaurant.location.latitude,
            restaurant.location.longitude
        )
        print(f"  • {restaurant.name} - {distance:.2f} km - Rating: {restaurant.rating}")
    
    # =========================
    # 4. PLACE ORDER
    # =========================
    print_section("4. Placing Orders")
    
    # Customer 1 orders from Restaurant 1 (has subscription - free delivery)
    print(f"{customer1.name} ordering from {restaurant1.name}...")
    
    order1 = order_service.create_order(
        customer_id=customer1.id,
        restaurant_id=restaurant1.id,
        items=[
            {'menu_item_id': item1.id, 'quantity': 2, 'special_instructions': 'Extra spicy'},
            {'menu_item_id': item3.id, 'quantity': 1}
        ],
        delivery_address=customer1.addresses[0]
    )
    
    print(f"✓ Order created: {order1.id}")
    print(f"  Status: {order1.status.value}")
    print(f"  Subtotal: ₹{order1.subtotal.amount}")
    print(f"  Delivery Fee: ₹{order1.delivery_fee.amount if not order1.is_subscription_order else 0.0} {'(FREE - Subscription)' if order1.is_subscription_order else ''}")
    print(f"  Tax: ₹{order1.tax.amount}")
    print(f"  Total: ₹{order1.total.amount}")
    print(f"  Loyalty Points to Earn: {order1.loyalty_points_earned}")
    
    # Customer 2 orders with loyalty points
    print(f"\n{customer2.name} ordering from {restaurant2.name}...")
    
    order2 = order_service.create_order(
        customer_id=customer2.id,
        restaurant_id=restaurant2.id,
        items=[
            {'menu_item_id': item4.id, 'quantity': 3}
        ],
        delivery_address=customer2.addresses[0]
    )
    
    # Apply loyalty points
    points_to_use = 50
    print(f"Applying {points_to_use} loyalty points...")
    order2 = order_service.apply_loyalty_discount(order2.id, points_to_use)
    
    print(f"✓ Order created: {order2.id}")
    print(f"  Total after discount: ₹{order2.total.amount}")
    print(f"  Loyalty points used: {order2.loyalty_points_used}")
    
    # Scheduled order
    print(f"\n{customer1.name} placing scheduled order...")
    scheduled_time = datetime.now() + timedelta(hours=2)
    order3 = order_service.create_order(
        customer_id=customer1.id,
        restaurant_id=restaurant1.id,
        items=[{'menu_item_id': item2.id, 'quantity': 1}],
        delivery_address=customer1.addresses[0],
        scheduled_for=scheduled_time
    )
    print(f"✓ Scheduled order created for: {scheduled_time.strftime('%I:%M %p')}")
    
    # =========================
    # 5. PROCESS PAYMENTS
    # =========================
    print_section("5. Processing Payments")
    
    from src.domain.enums.order_status import PaymentMethod
    
    # Payment for order 1
    payment1 = payment_service.create_payment(
        order_id=order1.id,
        amount=order1.total,
        payment_method=PaymentMethod.UPI
    )
    print(f"✓ Payment processed for Order {order1.id}")
    print(f"  Method: {payment1.payment_method.value}")
    print(f"  Status: {payment1.status.value}")
    print(f"  Transaction ID: {payment1.transaction_id}")
    
    # Payment for order 2
    payment2 = payment_service.create_payment(
        order_id=order2.id,
        amount=order2.total,
        payment_method=PaymentMethod.CARD
    )
    print(f"\n✓ Payment processed for Order {order2.id}")
    print(f"  Method: {payment2.payment_method.value}")
    print(f"  Transaction ID: {payment2.transaction_id}")
    
    # =========================
    # 6. ORDER STATE TRANSITIONS
    # =========================
    print_section("6. Order Lifecycle (State Machine)")
    
    print(f"Tracking Order {order1.id} through state transitions...\n")
    
    # Confirm order
    order1 = order_service.update_order_status(order1.id, OrderStatus.CONFIRMED)
    print(f"✓ {OrderStatus.CREATED.value} → {OrderStatus.CONFIRMED.value}")
    
    # Preparing
    order1 = order_service.update_order_status(order1.id, OrderStatus.PREPARING)
    print(f"✓ {OrderStatus.CONFIRMED.value} → {OrderStatus.PREPARING.value}")
    
    # Ready
    order1 = order_service.update_order_status(order1.id, OrderStatus.READY)
    print(f"✓ {OrderStatus.PREPARING.value} → {OrderStatus.READY.value}")
    
    # =========================
    # 7. ASSIGN DELIVERY PARTNER
    # =========================
    print_section("7. Delivery Partner Assignment (Strategy Pattern)")
    
    print("Finding available delivery partners...")
    available_partners = delivery_service.get_available_partners()
    print(f"Available partners: {len(available_partners)}")
    for p in available_partners:
        print(f"  • {p.name} - {p.vehicle_type.value} - Rating: {p.rating:.1f}")
    
    print(f"\nAssigning partner to Order {order1.id} using NEAREST strategy...")
    delivery1 = delivery_service.assign_partner_to_order(order1.id)
    
    assigned_partner = partner_repo.find_by_id(delivery1.delivery_partner_id)
    print(f"✓ Assigned: {assigned_partner.name}")
    print(f"  Status: {delivery1.status.value}")
    print(f"  Partner is now unavailable: {not assigned_partner.is_available}")
    
    # =========================
    # 8. TRACK DELIVERY
    # =========================
    print_section("8. Real-time Delivery Tracking")
    
    print(f"Tracking delivery for Order {order1.id}...\n")
    
    # Picked up
    order1 = order_service.update_order_status(order1.id, OrderStatus.PICKED_UP)
    delivery1 = delivery_service.mark_picked_up(delivery1.id)
    print(f"✓ Order Picked Up")
    print(f"  Delivery Status: {delivery1.get_current_status_display()}")
    
    # Update location (simulating GPS tracking)
    delivery1 = delivery_service.update_delivery_location(
        delivery1.id,
        12.9650,
        77.6000
    )
    print(f"✓ Location Updated: ({delivery1.current_location.latitude}, {delivery1.current_location.longitude})")
    
    # Delivered
    order1 = order_service.update_order_status(order1.id, OrderStatus.DELIVERED)
    delivery1 = delivery_service.mark_delivered(delivery1.id)
    print(f"✓ Order Delivered")
    print(f"  Delivery Status: {delivery1.get_current_status_display()}")
    
    # Check partner status
    assigned_partner = partner_repo.find_by_id(assigned_partner.id)
    print(f"  Partner available again: {assigned_partner.is_available}")
    print(f"  Total deliveries: {assigned_partner.total_deliveries}")
    
    # Check loyalty points awarded
    customer1_updated = customer_repo.find_by_id(customer1.id)
    print(f"\n✓ Loyalty points awarded to {customer1.name}: +{order1.loyalty_points_earned}")
    print(f"  Total loyalty points: {customer1_updated.loyalty_points}")
    
    # =========================
    # 9. REVIEWS AND RATINGS
    # =========================
    print_section("9. Reviews and Ratings")
    
    # Review restaurant
    restaurant_review = review_service.create_restaurant_review(
        customer_id=customer1.id,
        order_id=order1.id,
        restaurant_id=restaurant1.id,
        rating=4.5,
        comment="Excellent food, authentic taste!"
    )
    print(f"✓ Restaurant review submitted")
    print(f"  Rating: {restaurant_review.rating}")
    print(f"  Comment: \"{restaurant_review.comment}\"")
    print(f"  Verified: {restaurant_review.is_verified}")
    
    # Review delivery partner
    delivery_review = review_service.create_delivery_review(
        customer_id=customer1.id,
        order_id=order1.id,
        delivery_partner_id=assigned_partner.id,
        rating=5.0,
        comment="Very fast and professional delivery!"
    )
    print(f"\n✓ Delivery partner review submitted")
    print(f"  Rating: {delivery_review.rating}")
    print(f"  Comment: \"{delivery_review.comment}\"")
    
    # Check updated ratings
    restaurant1_updated = restaurant_repo.find_by_id(restaurant1.id)
    partner_updated = partner_repo.find_by_id(assigned_partner.id)
    
    print(f"\n✓ Updated Ratings:")
    print(f"  {restaurant1.name}: {restaurant1_updated.rating}")
    print(f"  {assigned_partner.name}: {partner_updated.rating:.1f}/5.0")
    
    # =========================
    # 10. ORDER CANCELLATION
    # =========================
    print_section("10. Order Cancellation")
    
    # Create a new order to cancel
    order_to_cancel = order_service.create_order(
        customer_id=customer2.id,
        restaurant_id=restaurant1.id,
        items=[{'menu_item_id': item1.id, 'quantity': 1}],
        delivery_address=customer2.addresses[0]
    )
    print(f"Created Order {order_to_cancel.id}")
    print(f"Status: {order_to_cancel.status.value}")
    
    # Cancel it
    cancelled_order = order_service.cancel_order(
        order_to_cancel.id,
        "Customer changed mind"
    )
    print(f"\n✓ Order cancelled")
    print(f"  New Status: {cancelled_order.status.value}")
    print(f"  Reason: {cancelled_order.cancellation_reason}")
    
    # Try invalid state transition (should fail)
    print(f"\nAttempting invalid state transition...")
    try:
        order_service.update_order_status(cancelled_order.id, OrderStatus.CONFIRMED)
    except Exception as e:
        print(f"✗ Prevented: {e}")
    
    # =========================
    # 11. STATISTICS
    # =========================
    print_section("11. Platform Statistics")
    
    total_customers = customer_repo.count()
    total_partners = partner_repo.count()
    total_restaurants = restaurant_repo.count()
    total_orders = order_repo.count()
    active_orders = len(order_repo.find_active_orders())
    total_deliveries = len([d for d in delivery_repo.find_all()])
    
    print(f"Platform Overview:")
    print(f"  Customers: {total_customers}")
    print(f"  Delivery Partners: {total_partners}")
    print(f"  Restaurants: {total_restaurants}")
    print(f"  Total Orders: {total_orders}")
    print(f"  Active Orders: {active_orders}")
    print(f"  Completed Deliveries: {total_deliveries}")
    
    print(f"\nSubscription Users:")
    active_subscribers = customer_repo.find_active_subscribers()
    print(f"  Active Subscriptions: {len(active_subscribers)}")
    for subscriber in active_subscribers:
        print(f"    • {subscriber.name} - {subscriber.subscription_plan.value}")
    
    print_section("DEMO COMPLETED SUCCESSFULLY!")
    print("All features demonstrated:")
    print("  ✓ User Management (Customers, Owners, Delivery Partners)")
    print("  ✓ Restaurant & Menu Management")
    print("  ✓ Geospatial Queries (Nearby Restaurants)")
    print("  ✓ Order Placement & State Machine")
    print("  ✓ Payment Processing (Multiple Methods)")
    print("  ✓ Delivery Partner Assignment (Strategy Pattern)")
    print("  ✓ Real-time Delivery Tracking")
    print("  ✓ Reviews & Ratings")
    print("  ✓ Order Cancellation")
    print("  ✓ Subscription Model (Free Delivery)")
    print("  ✓ Loyalty Points System")
    print("  ✓ Scheduled Orders")
    print()


if __name__ == "__main__":
    main()
