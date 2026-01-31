"""Pydantic schemas for API request/response models."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import (
    PaymentMethod,
    PaymentStatus,
    SpotType,
    TicketStatus,
    VehicleType,
)


# ============ Vehicle Schemas ============

class VehicleCreate(BaseModel):
    """Schema for vehicle creation."""
    license_plate: str = Field(..., min_length=3, max_length=20)
    vehicle_type: VehicleType
    owner_name: Optional[str] = Field(None, max_length=255)
    owner_phone: Optional[str] = Field(None, max_length=20)
    
    @field_validator('license_plate')
    @classmethod
    def validate_license_plate(cls, v: str) -> str:
        """Validate and normalize license plate."""
        return v.upper().replace(" ", "")


class VehicleResponse(BaseModel):
    """Schema for vehicle response."""
    id: UUID
    license_plate: str
    vehicle_type: VehicleType
    owner_name: Optional[str]
    owner_phone: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Parking Lot Schemas ============

class SpotCreate(BaseModel):
    """Schema for spot creation."""
    spot_number: str
    spot_type: SpotType
    is_charging_enabled: bool = False


class FloorCreate(BaseModel):
    """Schema for floor creation."""
    floor_number: int = Field(..., ge=1)
    spots: List[SpotCreate]


class ParkingLotCreate(BaseModel):
    """Schema for parking lot creation."""
    name: str = Field(..., min_length=1, max_length=255)
    address: str
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    zip_code: str = Field(..., max_length=20)
    floors: List[FloorCreate]


class ParkingLotResponse(BaseModel):
    """Schema for parking lot response."""
    id: UUID
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    total_floors: int
    total_spots: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParkingLotListResponse(BaseModel):
    """Schema for parking lot list."""
    lots: List[ParkingLotResponse]
    total: int
    page: int
    limit: int


# ============ Entry/Exit Schemas ============

class EntryRequest(BaseModel):
    """Schema for vehicle entry request."""
    vehicle: VehicleCreate
    preferred_spot_type: Optional[SpotType] = None
    is_valet: bool = False


class SpotInfo(BaseModel):
    """Schema for spot information."""
    spot_id: str
    spot_number: str
    floor_number: int
    spot_type: str


class TicketResponse(BaseModel):
    """Schema for ticket response."""
    id: UUID
    ticket_number: str
    spot: SpotInfo
    entry_time: datetime
    exit_time: Optional[datetime]
    status: TicketStatus
    is_valet: bool
    
    class Config:
        from_attributes = True


class EntryResponse(BaseModel):
    """Schema for entry response."""
    ticket: TicketResponse


class ExitRequest(BaseModel):
    """Schema for exit request."""
    ticket_number: str


class ChargeDetails(BaseModel):
    """Schema for charge details."""
    base_charge: float
    hourly_charge: float
    valet_charge: float = 0.0
    charging_fee: float = 0.0
    subtotal: float
    discount: float = 0.0
    total: float


class ExitResponse(BaseModel):
    """Schema for exit response."""
    ticket_id: UUID
    entry_time: str
    exit_time: str
    duration_hours: float
    charges: ChargeDetails
    payment_required: bool


# ============ Payment Schemas ============

class PaymentRequest(BaseModel):
    """Schema for payment request."""
    ticket_id: UUID
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    payment_method: PaymentMethod
    idempotency_key: str = Field(..., min_length=1, max_length=100)
    coupon_code: Optional[str] = Field(None, max_length=50)


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    payment_id: UUID
    ticket_id: UUID
    amount: Decimal
    discount: Decimal = Decimal('0.00')
    final_amount: Decimal
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: Optional[str]
    paid_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ Availability Schemas ============

class SpotTypeAvailability(BaseModel):
    """Schema for spot type availability."""
    total: int
    available: int
    occupied: int


class FloorAvailability(BaseModel):
    """Schema for floor availability."""
    floor_number: int
    total_spots: int
    available_spots: int


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""
    lot_id: str
    lot_name: str
    total_spots: int
    available_spots: int
    occupancy_rate: float
    availability_by_type: dict
    availability_by_floor: List[FloorAvailability]
