"""Parking entry/exit endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import (
    ChargeDetails,
    EntryRequest,
    EntryResponse,
    ExitRequest,
    ExitResponse,
    SpotInfo,
    TicketResponse,
)
from src.application.services.parking_service import ParkingService
from src.application.services.pricing_service import PricingService
from src.infrastructure.database.connection import get_db

router = APIRouter()


@router.post("/parking-lots/{lot_id}/entry", response_model=EntryResponse, status_code=201)
def vehicle_entry(
    lot_id: UUID,
    entry_data: EntryRequest,
    db: Session = Depends(get_db)
):
    """Process vehicle entry and allocate parking spot.
    
    Args:
        lot_id: Parking lot ID
        entry_data: Entry request data
        db: Database session
        
    Returns:
        Entry response with ticket and spot info
    """
    parking_service = ParkingService(db)
    
    try:
        ticket, spot_info = parking_service.process_entry(
            parking_lot_id=lot_id,
            license_plate=entry_data.vehicle.license_plate,
            vehicle_type=entry_data.vehicle.vehicle_type,
            owner_name=entry_data.vehicle.owner_name,
            owner_phone=entry_data.vehicle.owner_phone,
            preferred_spot_type=entry_data.preferred_spot_type,
            is_valet=entry_data.is_valet
        )
        
        return EntryResponse(
            ticket=TicketResponse(
                id=ticket.id,
                ticket_number=ticket.ticket_number,
                spot=SpotInfo(**spot_info),
                entry_time=ticket.entry_time,
                exit_time=ticket.exit_time,
                status=ticket.status,
                is_valet=ticket.is_valet
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/parking-lots/{lot_id}/exit", response_model=ExitResponse)
def vehicle_exit(
    lot_id: UUID,
    exit_data: ExitRequest,
    db: Session = Depends(get_db)
):
    """Process vehicle exit and calculate parking charges.
    
    Args:
        lot_id: Parking lot ID
        exit_data: Exit request data
        db: Database session
        
    Returns:
        Exit response with charges
    """
    parking_service = ParkingService(db)
    pricing_service = PricingService(db)
    
    try:
        # Process exit
        ticket, charge_info = parking_service.process_exit(exit_data.ticket_number)
        
        # Calculate charges
        is_ev_charging = False
        spot = db.query(type(ticket.spot)).get(ticket.spot_id)
        if spot:
            is_ev_charging = spot.is_charging_enabled
        
        charges = pricing_service.calculate_charges(
            parking_lot_id=lot_id,
            spot_id=ticket.spot_id,
            duration_hours=charge_info['duration_hours'],
            is_valet=ticket.is_valet,
            is_ev_charging=is_ev_charging
        )
        
        charge_info['charges'] = ChargeDetails(**charges)
        
        return ExitResponse(**charge_info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """Get ticket details.
    
    Args:
        ticket_id: Ticket ID
        db: Database session
        
    Returns:
        Ticket details
    """
    parking_service = ParkingService(db)
    ticket = parking_service.get_ticket_details(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    spot = ticket.spot
    spot_info = SpotInfo(
        spot_id=str(spot.id),
        spot_number=spot.spot_number,
        floor_number=spot.floor.floor_number,
        spot_type=spot.spot_type.value
    )
    
    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        spot=spot_info,
        entry_time=ticket.entry_time,
        exit_time=ticket.exit_time,
        status=ticket.status,
        is_valet=ticket.is_valet
    )
