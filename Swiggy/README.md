# Food Delivery Platform - Low-Level Design

A production-grade food delivery platform implementation (similar to Swiggy/Zomato) in Python, showcasing clean architecture principles, design patterns, and best practices.

## 🏗️ Architecture

### Layered Architecture
- **Domain Layer**: Core business entities and logic
- **Repository Layer**: Data access abstraction using Repository pattern
- **Service Layer**: Business logic orchestration
- **Infrastructure Layer**: Cross-cutting concerns

### Design Patterns
- **Repository Pattern**: Abstract data access
- **State Machine Pattern**: Order lifecycle management
- **Strategy Pattern**: Delivery partner assignment algorithms
- **Factory Pattern**: Payment gateway selection
- **Value Objects**: Immutable domain objects (Location, Money, Rating)

## 🚀 Features

### Core Features
- ✅ User management (Customers, Restaurant Owners, Delivery Partners)
- ✅ Restaurant and menu management
- ✅ Order placement with state machine
- ✅ Real-time delivery tracking
- ✅ Multiple payment methods (Cash, Card, UPI, Wallet)
- ✅ Reviews and ratings
- ✅ Geospatial queries for nearby restaurants

### Extension Features
- ✅ Subscription model (unlimited free delivery)
- ✅ Loyalty points system
- ✅ Scheduled orders for later delivery
- ✅ Concurrent order handling with optimistic locking
- ✅ Payment idempotency

## 📁 Project Structure

```
Swiggy/
├── src/
│   ├── domain/
│   │   ├── models/          # Domain entities
│   │   │   ├── user.py
│   │   │   ├── restaurant.py
│   │   │   ├── order.py
│   │   │   ├── delivery.py
│   │   │   ├── payment.py
│   │   │   └── review.py
│   │   ├── enums/           # Enumerations
│   │   ├── exceptions.py    # Domain exceptions
│   │   └── value_objects.py # Value objects
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── run_demo.py              # Comprehensive demo
└── requirements.txt
```

## 🛠️ Installation

```bash
cd /Users/princeraj/Desktop/Optimus/HandsOnProjects/LLD/Swiggy

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Running the Demo

```bash
# Run comprehensive demo
python run_demo.py
```

The demo script demonstrates:
1. Creating users (customers, owners, delivery partners)
2. Setting up restaurants with menus
3. Browsing nearby restaurants (geospatial queries)
4. Placing orders with various scenarios
5. Processing payments
6. Order state transitions (state machine)
7. Delivery partner assignment (strategy pattern)
8. Real-time delivery tracking
9. Reviews and ratings
10. Order cancellation
11. Platform statistics

## 🎯 Key Design Decisions

### Order State Machine
Orders follow a strict state machine with validated transitions:
```
CREATED → CONFIRMED → PREPARING → READY → PICKED_UP → DELIVERED
         ↓
      CANCELLED
```

### Delivery Partner Assignment
Multiple strategies available:
- **Nearest Partner**: Proximity-based assignment
- **Rating-based**: Highest-rated partner
- **Load Balancing**: Distribute orders evenly

### Concurrent Order Handling
- Optimistic locking with version fields
- Prevents overselling and race conditions

### Payment Processing
- Factory pattern for multiple payment gateways
- Idempotency keys prevent duplicate charges
- Supports refunds

### Geospatial Queries
- Haversine formula for distance calculation
- Find nearby restaurants efficiently
- Delivery time estimation

## 📊 Domain Models

### User Hierarchy
- **Customer**: Has addresses, loyalty points, subscription
- **Restaurant Owner**: Manages multiple restaurants
- **Delivery Partner**: Has location, vehicle type, availability status

### Order Management
- **Order**: State machine, payments, delivery tracking
- **OrderItem**: Individual items with quantities
- **Delivery**: Real-time location tracking

### Restaurant Structure
- **Restaurant**: Location, ratings, operating hours
- **MenuCategory**: Organized menu sections
- **MenuItem**: Prices, availability, preparation time

## 🔄 Order Lifecycle

```
1. Customer browses nearby restaurants
2. Adds items to cart
3. Places order (CREATED)
4. Payment processed
5. Restaurant confirms (CONFIRMED)
6. Food preparation (PREPARING)
7. Order ready (READY)
8. Delivery partner assigned
9. Partner picks up order (PICKED_UP)
10. Partner delivers (DELIVERED)
11. Customer leaves review
12. Loyalty points awarded
```

## 💡 Extension Scenarios Implemented

### 1. Subscription Model
- Monthly/Quarterly/Yearly plans
- Free delivery for active subscribers
- Automatic expiry handling

### 2. Loyalty Points
- Earn points on order completion (1% of total)
- Redeem points for discounts (1 point = ₹0.10)
- Track point history

### 3. Scheduled Orders
- Order for future delivery
- Background processing for scheduled orders
- Automatic confirmation at scheduled time

## 🧪 Production-Grade Features

- **SOLID Principles**: Clear separation of concerns
- **Clean Architecture**: Domain-driven design
- **Design Patterns**: Repository, Strategy, Factory, State Machine
- **Immutable Value Objects**: Location, Money, Rating
- **Type Safety**: Type hints throughout
- **Exception Handling**: Custom domain exceptions
- **Concurrency Control**: Optimistic locking
- **Idempotency**: Payment processing
- **Validation**: Business rule enforcement

## 📈 Scalability Considerations

The current implementation uses in-memory storage for demonstration. For production:

1. **Database**: Replace repositories with SQLAlchemy/PostgreSQL
2. **Caching**: Add Redis for frequently accessed data
3. **Message Queue**: RabbitMQ/Kafka for async processing
4. **Geospatial**: Use PostGIS for efficient location queries
5. **Load Balancing**: Distribute API requests
6. **Microservices**: Split into smaller services

## 👨‍💻 Code Quality

- Clean, readable code with comprehensive docstrings
- Type hints for better IDE support
- Separation of concerns across layers
- Business logic isolated in domain layer
- Easy to test and extend

## 📝 License

This is a demonstration project for educational purposes.
