"""Ticket domain model."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.base_entity import BaseEntity
from src.domain.enums import TicketStatus


class Ticket(BaseEntity):
    """Ticket entity representing a parking session."""
    
    def __init__(
        self,
        ticket_number: str,
        parking_lot_id: UUID,
        spot_id: UUID,
        vehicle_id: UUID,
        entry_time: datetime,
        status: TicketStatus = TicketStatus.ACTIVE,
        exit_time: Optional[datetime] = None,
        is_valet: bool = False,
        id: Optional[UUID] = None
    ):
        """Initialize ticket.
        
        Args:
            ticket_number: Unique ticket identifier
            parking_lot_id: ID of parking lot
            spot_id: ID of assigned parking spot
            vehicle_id: ID of vehicle
            entry_time: Time of entry
            status: Current ticket status
            exit_time: Time of exit (if applicable)
            is_valet: Whether this is a valet parking ticket
            id: Optional UUID identifier
        """
        super().__init__(id)
        self.ticket_number = ticket_number
        self.parking_lot_id = parking_lot_id
        self.spot_id = spot_id
        self.vehicle_id = vehicle_id
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.status = status
        self.is_valet = is_valet
    
    def is_active(self) -> bool:
        """Check if ticket is active.
        
        Returns:
            True if ticket is active, False otherwise
        """
        return self.status == TicketStatus.ACTIVE
    
    def mark_as_paid(self) -> None:
        """Mark ticket as paid.
        
        Raises:
            ValueError: If ticket is not active
        """
        if not self.is_active():
            raise ValueError(f"Ticket {self.ticket_number} is not active")
        self.status = TicketStatus.PAID
        self.update_timestamp()
    
    def mark_as_lost(self) -> None:
        """Mark ticket as lost."""
        self.status = TicketStatus.LOST
        self.update_timestamp()
    
    def cancel(self) -> None:
        """Cancel ticket."""
        self.status = TicketStatus.CANCELLED
        self.update_timestamp()
    
    def set_exit_time(self, exit_time: datetime) -> None:
        """Set exit time for the ticket.
        
        Args:
            exit_time: Exit timestamp
            
        Raises:
            ValueError: If exit time is before entry time
        """
        if exit_time < self.entry_time:
            raise ValueError("Exit time cannot be before entry time")
        self.exit_time = exit_time
        self.update_timestamp()
    
    def get_duration_hours(self) -> float:
        """Calculate parking duration in hours.
        
        Returns:
            Duration in hours, or 0 if not yet exited
        """
        if not self.exit_time:
            # Calculate current duration if still parked
            duration = datetime.utcnow() - self.entry_time
        else:
            duration = self.exit_time - self.entry_time
        
        # Convert to hours (round up to nearest 0.01 hour)
        hours = duration.total_seconds() / 3600
        return round(hours, 2)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Ticket(number={self.ticket_number}, status={self.status.value}, "
            f"duration_hours={self.get_duration_hours()})"
        )
