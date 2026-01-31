"""Parking service for vehicle entry/exit."""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.enums import SpotStatus, SpotType, TicketStatus, VehicleType
from src.domain.models.vehicle import Vehicle
from src.domain.patterns.observer import Subject
from src.infrastructure.database.models import TicketModel
from src.infrastructure.repository.parking_repository import ParkingSpotRepository
from src.infrastructure.repository.ticket_repository import TicketRepository, VehicleRepository


class ParkingService(Subject):
    """Service for managing vehicle entry and exit."""
    
    def __init__(self, db: Session):
        """Initialize parking service.
        
        Args:
            db: Database session
        """
        super().__init__()
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.ticket_repo = TicketRepository(db)
        self.spot_repo = ParkingSpotRepository(db)
    
    def process_entry(
        self,
        parking_lot_id: UUID,
        license_plate: str,
        vehicle_type: VehicleType,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
        preferred_spot_type: Optional[SpotType] = None,
        is_valet: bool = False
    ) -> Tuple[TicketModel, Dict]:
        """Process vehicle entry and allocate spot.
        
        Args:
            parking_lot_id: Parking lot ID
            license_plate: Vehicle license plate
            vehicle_type: Type of vehicle
            owner_name: Vehicle owner name
            owner_phone: Owner contact
            preferred_spot_type: Preferred spot type
            is_valet: Whether this is valet parking
            
        Returns:
            Tuple of (ticket, spot_info)
            
        Raises:
            ValueError: If no spots available or vehicle already parked
        """
        # Check for active tickets for this vehicle
        vehicle = self.vehicle_repo.get_by_license_plate(license_plate)
        if vehicle:
            active_tickets = [
                t for t in self.ticket_repo.get_tickets_by_vehicle(vehicle.id, limit=1)
                if t.status == TicketStatus.ACTIVE
            ]
            if active_tickets:
                raise ValueError(
                    f"Vehicle {license_plate} already has an active ticket"
                )
        
        # Get or create vehicle
        vehicle = self.vehicle_repo.get_or_create(
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
            owner_phone=owner_phone
        )
        
        # Create domain vehicle to get compatible spots
        domain_vehicle = Vehicle(
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
            owner_phone=owner_phone,
            id=vehicle.id
        )
        compatible_spots = domain_vehicle.get_compatible_spot_types()
        
        # Find available spot
        spot = self.spot_repo.find_available_spot_for_vehicle(
            parking_lot_id=parking_lot_id,
            compatible_spot_types=compatible_spots,
            preferred_type=preferred_spot_type
        )
        
        if not spot:
            raise ValueError("No available spots for this vehicle type")
        
        # Try to occupy spot with optimistic locking
        max_retries = 3
        for attempt in range(max_retries):
            if self.spot_repo.occupy_spot_with_lock(spot.id):
                break
            
            # If failed, try to find another spot
            spot = self.spot_repo.find_available_spot_for_vehicle(
                parking_lot_id=parking_lot_id,
                compatible_spot_types=compatible_spots,
                preferred_type=preferred_spot_type
            )
            
            if not spot:
                raise ValueError("No available spots (concurrency conflict)")
            
            if attempt == max_retries - 1:
                raise ValueError("Failed to allocate spot after retries")
        
        # Generate ticket
        ticket_number = self.ticket_repo.generate_ticket_number(parking_lot_id)
        ticket = TicketModel(
            ticket_number=ticket_number,
            parking_lot_id=parking_lot_id,
            spot_id=spot.id,
            vehicle_id=vehicle.id,
            entry_time=datetime.utcnow(),
            status=TicketStatus.ACTIVE,
            is_valet=is_valet
        )
        ticket = self.ticket_repo.create(ticket)
        
        # Notify observers about spot occupation
        self.notify({
            'event_type': 'spot_occupied',
            'parking_lot_id': str(parking_lot_id),
            'spot_id': str(spot.id),
            'spot_number': spot.spot_number,
            'spot_type': spot.spot_type.value
        })
        
        # Get floor number for response
        spot_info = {
            'spot_id': str(spot.id),
            'spot_number': spot.spot_number,
            'floor_number': spot.floor.floor_number,
            'spot_type': spot.spot_type.value
        }
        
        self.db.commit()
        return ticket, spot_info
    
    def process_exit(
        self,
        ticket_number: str
    ) -> Tuple[TicketModel, Dict]:
        """Process vehicle exit and calculate charges.
        
        Args:
            ticket_number: Ticket number
            
        Returns:
            Tuple of (ticket, charge_info)
            
        Raises:
            ValueError: If ticket not found or already processed
        """
        # Get ticket
        ticket = self.ticket_repo.get_by_ticket_number(ticket_number)
        if not ticket:
            raise ValueError(f"Ticket {ticket_number} not found")
        
        if ticket.status != TicketStatus.ACTIVE:
            raise ValueError(f"Ticket {ticket_number} is not active")
        
        # Set exit time
        exit_time = datetime.utcnow()
        ticket.exit_time = exit_time
        
        # Calculate duration
        duration = exit_time - ticket.entry_time
        duration_hours = round(duration.total_seconds() / 3600, 2)
        
        # The actual pricing will be calculated by PricingService
        # Here we just prepare the data
        charge_info = {
            'entry_time': ticket.entry_time.isoformat(),
            'exit_time': exit_time.isoformat(),
            'duration_hours': duration_hours,
            'payment_required': True
        }
        
        self.db.commit()
        return ticket, charge_info
    
    def complete_exit(self, ticket_id: UUID) -> None:
        """Complete exit process after payment.
        
        Args:
            ticket_id: Ticket ID
            
        Raises:
            ValueError: If ticket not found
        """
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        # Vacate spot
        self.spot_repo.vacate_spot(ticket.spot_id)
        
        # Notify observers about spot availability
        spot = self.spot_repo.get_by_id(ticket.spot_id)
        self.notify({
            'event_type': 'spot_available',
            'parking_lot_id': str(ticket.parking_lot_id),
            'spot_id': str(spot.id),
            'spot_number': spot.spot_number,
            'spot_type': spot.spot_type.value
        })
        
        self.db.commit()
    
    def get_ticket_details(self, ticket_id: UUID) -> Optional[TicketModel]:
        """Get ticket details.
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            TicketModel or None
        """
        return self.ticket_repo.get_by_id(ticket_id)
