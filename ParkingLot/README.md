# Parking Lot Management System

A production-ready parking lot management system built with Python, FastAPI, and PostgreSQL.

## Features

- 🚗 **Multi-level Parking**: Support for multiple parking lots with floors and different spot types
- 🔒 **Concurrent Safety**: Thread-safe spot allocation with optimistic locking
- 💳 **Payment Processing**: Idempotent payment handling with multiple payment methods
- 📊 **Real-time Availability**: Instant availability updates using Observer pattern
- ⚡ **EV Charging**: Support for electric vehicle charging spots
- 🎟️ **Reservations**: Monthly and hourly parking reservations
- 💰 **Dynamic Pricing**: Demand-based pricing with coupon support
- 🚙 **Valet Service**: Valet parking workflow integration
- 📝 **Audit Trail**: Complete transaction history logging

## Architecture

```
src/
├── domain/              # Domain models and business logic
│   ├── models/          # Entity classes
│   └── patterns/        # Design pattern implementations
├── application/         # Service layer
│   └── services/        # Business services
├── infrastructure/      # External concerns
│   ├── database/        # Database models and connections
│   └── repository/      # Data access layer
├── api/                 # API layer
│   ├── routers/         # Route handlers
│   └── schemas/         # Request/Response models
├── extensions/          # Extension features
└── utils/               # Utilities
```

## Design Patterns

- **Factory Pattern**: Spot creation
- **Strategy Pattern**: Pricing strategies
- **Observer Pattern**: Availability notifications
- **Repository Pattern**: Data access abstraction
- **Singleton Pattern**: Parking lot manager

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation

```bash
# Clone the repository
cd /Users/princeraj/Desktop/Optimus/HandsOnProjects/LLD/ParkingLot

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/domain/ -v

# Run concurrent allocation stress test
pytest tests/stress/test_concurrent_allocation.py -v -n 10
```

## Database Schema

See [implementation_plan.md](/.gemini/antigravity/brain/eda3ac30-02bf-4345-9118-9e4c11e945ca/implementation_plan.md) for complete schema details.

## API Endpoints

### Parking Lot Management
- `POST /api/v1/parking-lots` - Create parking lot
- `GET /api/v1/parking-lots` - List parking lots
- `GET /api/v1/parking-lots/{lotId}` - Get lot details
- `GET /api/v1/parking-lots/{lotId}/availability` - Get availability

### Vehicle Entry/Exit
- `POST /api/v1/parking-lots/{lotId}/entry` - Vehicle entry
- `POST /api/v1/parking-lots/{lotId}/exit` - Vehicle exit
- `GET /api/v1/tickets/{ticketId}` - Get ticket details

### Payments
- `POST /api/v1/payments` - Process payment
- `GET /api/v1/payments/{paymentId}` - Get payment details

## License

MIT
