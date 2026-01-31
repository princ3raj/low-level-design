"""SQLAlchemy ORM models."""
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.domain.enums import (
    DiscountType,
    PaymentMethod,
    PaymentStatus,
    ReservationStatus,
    ReservationType,
    SpotStatus,
    SpotType,
    TicketStatus,
    VehicleType,
)
from src.infrastructure.database.connection import Base


class ParkingLotModel(Base):
    """SQLAlchemy model for parking_lots table."""
    
    __tablename__ = "parking_lots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    total_floors = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    floors = relationship("FloorModel", back_populates="parking_lot", cascade="all, delete-orphan")
    tickets = relationship("TicketModel", back_populates="parking_lot")
    pricing_rules = relationship("PricingRuleModel", back_populates="parking_lot")


class FloorModel(Base):
    """SQLAlchemy model for floors table."""
    
    __tablename__ = "floors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    parking_lot_id = Column(UUID(as_uuid=True), ForeignKey("parking_lots.id"), nullable=False)
    floor_number = Column(Integer, nullable=False)
    total_spots = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    parking_lot = relationship("ParkingLotModel", back_populates="floors")
    spots = relationship("ParkingSpotModel", back_populates="floor", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("parking_lot_id", "floor_number", name="uq_parking_lot_floor"),
    )


class ParkingSpotModel(Base):
    """SQLAlchemy model for parking_spots table."""
    
    __tablename__ = "parking_spots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    floor_id = Column(UUID(as_uuid=True), ForeignKey("floors.id"), nullable=False)
    spot_number = Column(String(20), nullable=False)
    spot_type = Column(SQLEnum(SpotType), nullable=False)
    status = Column(SQLEnum(SpotStatus), default=SpotStatus.AVAILABLE, nullable=False)
    is_charging_enabled = Column(Boolean, default=False)
    version = Column(Integer, default=0, nullable=False)  # For optimistic locking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    floor = relationship("FloorModel", back_populates="spots")
    tickets = relationship("TicketModel", back_populates="spot")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint("floor_id", "spot_number", name="uq_floor_spot_number"),
        Index("idx_floor_status_type", "floor_id", "status", "spot_type"),
    )


class VehicleModel(Base):
    """SQLAlchemy model for vehicles table."""
    
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    license_plate = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)
    owner_name = Column(String(255))
    owner_phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tickets = relationship("TicketModel", back_populates="vehicle")


class TicketModel(Base):
    """SQLAlchemy model for tickets table."""
    
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ticket_number = Column(String(50), unique=True, nullable=False)
    parking_lot_id = Column(UUID(as_uuid=True), ForeignKey("parking_lots.id"), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("parking_spots.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    is_valet = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    parking_lot = relationship("ParkingLotModel", back_populates="tickets")
    spot = relationship("ParkingSpotModel", back_populates="tickets")
    vehicle = relationship("VehicleModel", back_populates="tickets")
    payments = relationship("PaymentModel", back_populates="ticket")
    
    # Indexes
    __table_args__ = (
        Index("idx_ticket_number", "ticket_number"),
        Index("idx_status_entry_time", "status", "entry_time"),
    )


class PaymentModel(Base):
    """SQLAlchemy model for payments table."""
    
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    transaction_id = Column(String(100), unique=True)
    idempotency_key = Column(String(100), unique=True, nullable=False)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = relationship("TicketModel", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index("idx_idempotency_key", "idempotency_key"),
        Index("idx_transaction_id", "transaction_id"),
    )


class PricingRuleModel(Base):
    """SQLAlchemy model for pricing_rules table."""
    
    __tablename__ = "pricing_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    parking_lot_id = Column(UUID(as_uuid=True), ForeignKey("parking_lots.id"), nullable=False)
    spot_type = Column(SQLEnum(SpotType), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    daily_max = Column(Numeric(10, 2))
    is_dynamic = Column(Boolean, default=False)
    demand_multiplier = Column(Numeric(3, 2), default=1.0)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    parking_lot = relationship("ParkingLotModel", back_populates="pricing_rules")
    
    # Indexes
    __table_args__ = (
        Index("idx_lot_spottype_validity", "parking_lot_id", "spot_type", "valid_from", "valid_until"),
    )


class ReservationModel(Base):
    """SQLAlchemy model for reservations table."""
    
    __tablename__ = "reservations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    parking_lot_id = Column(UUID(as_uuid=True), ForeignKey("parking_lots.id"), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("parking_spots.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True))
    reservation_type = Column(SQLEnum(ReservationType), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ReservationStatus), default=ReservationStatus.ACTIVE, nullable=False)
    amount_paid = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_spot_time_range", "spot_id", "start_time", "end_time"),
    )


class CouponModel(Base):
    """SQLAlchemy model for coupons table."""
    
    __tablename__ = "coupons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(SQLEnum(DiscountType), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)
    min_amount = Column(Numeric(10, 2))
    max_discount = Column(Numeric(10, 2))
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    usage_limit = Column(Integer)
    times_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    usage_records = relationship("CouponUsageModel", back_populates="coupon")


class CouponUsageModel(Base):
    """SQLAlchemy model for coupon_usage table."""
    
    __tablename__ = "coupon_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    discount_applied = Column(Numeric(10, 2), nullable=False)
    used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    coupon = relationship("CouponModel", back_populates="usage_records")


class AuditLogModel(Base):
    """SQLAlchemy model for audit_logs table."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    user_id = Column(UUID(as_uuid=True))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_entity_type_id_time", "entity_type", "entity_id", "created_at"),
    )
