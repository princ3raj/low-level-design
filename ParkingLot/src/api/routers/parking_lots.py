"""Parking lot management endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas import (
    AvailabilityResponse,
    ParkingLotCreate,
    ParkingLotListResponse,
    ParkingLotResponse,
)
from src.application.services.availability_service import AvailabilityService
from src.domain.patterns.factory import SpotFactory
from src.infrastructure.database.connection import get_db
from src.infrastructure.database.models import FloorModel, ParkingLotModel
from src.infrastructure.repository.parking_repository import (
    ParkingLotRepository,
    ParkingSpotRepository,
)

router = APIRouter()


@router.post("/parking-lots", response_model=ParkingLotResponse, status_code=201)
def create_parking_lot(
    lot_data: ParkingLotCreate,
    db: Session = Depends(get_db)
):
    """Create a new parking lot.
    
    Args:
        lot_data: Parking lot creation data
        db: Database session
        
    Returns:
        Created parking lot
    """
    lot_repo = ParkingLotRepository(db)
    
    # Check if lot with same name exists
    existing = lot_repo.get_by_name(lot_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Parking lot with this name already exists")
    
    # Create parking lot
    parking_lot = ParkingLotModel(
        name=lot_data.name,
        address=lot_data.address,
        city=lot_data.city,
        state=lot_data.state,
        zip_code=lot_data.zip_code,
        total_floors=len(lot_data.floors)
    )
    parking_lot = lot_repo.create(parking_lot)
    
    # Create floors and spots
    total_spots = 0
    for floor_data in lot_data.floors:
        floor = FloorModel(
            parking_lot_id=parking_lot.id,
            floor_number=floor_data.floor_number,
            total_spots=len(floor_data.spots)
        )
        db.add(floor)
        db.flush()
        
        # Create spots using factory
        for spot_data in floor_data.spots:
            spot = SpotFactory.create_spot(
                spot_number=spot_data.spot_number,
                spot_type=spot_data.spot_type,
                floor_id=floor.id
            )
            if spot_data.is_charging_enabled:
                spot.is_charging_enabled = True
            db.add(spot)
        
        total_spots += floor.total_spots
    
    parking_lot.total_floors = len(lot_data.floors)
    db.commit()
    db.refresh(parking_lot)
    
    return ParkingLotResponse(
        id=parking_lot.id,
        name=parking_lot.name,
        address=parking_lot.address,
        city=parking_lot.city,
        state=parking_lot.state,
        zip_code=parking_lot.zip_code,
        total_floors=parking_lot.total_floors,
        total_spots=total_spots,
        created_at=parking_lot.created_at
    )


@router.get("/parking-lots", response_model=ParkingLotListResponse)
def list_parking_lots(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all parking lots with pagination.
    
    Args:
        page: Page number
        limit: Items per page
        city: Optional city filter
        db: Database session
        
    Returns:
        List of parking lots
    """
    lot_repo = ParkingLotRepository(db)
    skip = (page - 1) * limit
    
    if city:
        lots = lot_repo.get_by_city(city, skip=skip, limit=limit)
        total = db.query(ParkingLotModel).filter(ParkingLotModel.city == city).count()
    else:
        lots = lot_repo.get_all(skip=skip, limit=limit)
        total = lot_repo.count()
    
    # Convert to response models
    lot_responses = []
    for lot in lots:
        # Calculate total spots
        total_spots = sum(floor.total_spots for floor in lot.floors)
        lot_responses.append(ParkingLotResponse(
            id=lot.id,
            name=lot.name,
            address=lot.address,
            city=lot.city,
            state=lot.state,
            zip_code=lot.zip_code,
            total_floors=lot.total_floors,
            total_spots=total_spots,
            created_at=lot.created_at
        ))
    
    return ParkingLotListResponse(
        lots=lot_responses,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/parking-lots/{lot_id}", response_model=ParkingLotResponse)
def get_parking_lot(
    lot_id: UUID,
    db: Session = Depends(get_db)
):
    """Get parking lot details.
    
    Args:
        lot_id: Parking lot ID
        db: Database session
        
    Returns:
        Parking lot details
    """
    lot_repo = ParkingLotRepository(db)
    lot = lot_repo.get_with_floors(lot_id)
    
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")
    
    total_spots = sum(floor.total_spots for floor in lot.floors)
    
    return ParkingLotResponse(
        id=lot.id,
        name=lot.name,
        address=lot.address,
        city=lot.city,
        state=lot.state,
        zip_code=lot.zip_code,
        total_floors=lot.total_floors,
        total_spots=total_spots,
        created_at=lot.created_at
    )


@router.get("/parking-lots/{lot_id}/availability", response_model=AvailabilityResponse)
def get_availability(
    lot_id: UUID,
    db: Session = Depends(get_db)
):
    """Get real-time availability for a parking lot.
    
    Args:
        lot_id: Parking lot ID
        db: Database session
        
    Returns:
        Availability details
    """
    availability_service = AvailabilityService(db)
    
    try:
        availability = availability_service.get_availability(lot_id)
        return AvailabilityResponse(**availability)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
