"""Ticket and payment repositories."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.domain.enums import PaymentStatus, TicketStatus
from src.infrastructure.database.models import PaymentModel, TicketModel, VehicleModel
from src.infrastructure.repository.base_repository import BaseRepository


class VehicleRepository(BaseRepository[VehicleModel]):
    """Repository for vehicles."""
    
    def __init__(self, db: Session):
        """Initialize vehicle repository."""
        super().__init__(VehicleModel, db)
    
    def get_by_license_plate(self, license_plate: str) -> Optional[VehicleModel]:
        """Get vehicle by license plate.
        
        Args:
            license_plate: Vehicle license plate
            
        Returns:
            VehicleModel or None
        """
        return self.db.query(self.model).filter(
            self.model.license_plate == license_plate
        ).first()
    
    def get_or_create(
        self,
        license_plate: str,
        vehicle_type,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None
    ) -> VehicleModel:
        """Get existing vehicle or create new one.
        
        Args:
            license_plate: Vehicle license plate
            vehicle_type: Vehicle type enum
            owner_name: Owner name
            owner_phone: Owner phone
            
        Returns:
            VehicleModel
        """
        vehicle = self.get_by_license_plate(license_plate)
        if vehicle:
            # Update owner info if provided
            if owner_name:
                vehicle.owner_name = owner_name
            if owner_phone:
                vehicle.owner_phone = owner_phone
            self.db.flush()
            return vehicle
        
        # Create new vehicle
        vehicle = VehicleModel(
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
            owner_phone=owner_phone
        )
        return self.create(vehicle)


class TicketRepository(BaseRepository[TicketModel]):
    """Repository for tickets."""
    
    def __init__(self, db: Session):
        """Initialize ticket repository."""
        super().__init__(TicketModel, db)
    
    def get_by_ticket_number(self, ticket_number: str) -> Optional[TicketModel]:
        """Get ticket by ticket number.
        
        Args:
            ticket_number: Ticket number
            
        Returns:
            TicketModel or None
        """
        return self.db.query(self.model).filter(
            self.model.ticket_number == ticket_number
        ).first()
    
    def get_active_tickets(
        self,
        parking_lot_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TicketModel]:
        """Get active tickets.
        
        Args:
            parking_lot_id: Optional parking lot filter
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of active tickets
        """
        query = self.db.query(self.model).filter(
            self.model.status == TicketStatus.ACTIVE
        )
        
        if parking_lot_id:
            query = query.filter(self.model.parking_lot_id == parking_lot_id)
        
        return query.order_by(
            self.model.entry_time.desc()
        ).offset(skip).limit(limit).all()
    
    def get_tickets_by_vehicle(
        self,
        vehicle_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[TicketModel]:
        """Get tickets for a vehicle.
        
        Args:
            vehicle_id: Vehicle ID
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of tickets
        """
        return self.db.query(self.model).filter(
            self.model.vehicle_id == vehicle_id
        ).order_by(
            self.model.entry_time.desc()
        ).offset(skip).limit(limit).all()
    
    def generate_ticket_number(self, parking_lot_id: UUID) -> str:
        """Generate unique ticket number.
        
        Args:
            parking_lot_id: Parking lot ID
            
        Returns:
            Unique ticket number
        """
        from datetime import datetime
        
        # Format: TKT-YYYYMMDD-NNNN
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Count tickets created today for this lot
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        count = self.db.query(self.model).filter(
            and_(
                self.model.parking_lot_id == parking_lot_id,
                self.model.created_at >= today_start
            )
        ).count()
        
        return f"TKT-{date_str}-{count + 1:04d}"


class PaymentRepository(BaseRepository[PaymentModel]):
    """Repository for payments."""
    
    def __init__(self, db: Session):
        """Initialize payment repository."""
        super().__init__(PaymentModel, db)
    
    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[PaymentModel]:
        """Get payment by idempotency key.
        
        This supports idempotent payment processing.
        
        Args:
            idempotency_key: Unique idempotency key
            
        Returns:
            PaymentModel or None
        """
        return self.db.query(self.model).filter(
            self.model.idempotency_key == idempotency_key
        ).first()
    
    def get_by_transaction_id(self, transaction_id: str) -> Optional[PaymentModel]:
        """Get payment by transaction ID.
        
        Args:
            transaction_id: External transaction ID
            
        Returns:
            PaymentModel or None
        """
        return self.db.query(self.model).filter(
            self.model.transaction_id == transaction_id
        ).first()
    
    def get_payments_by_ticket(self, ticket_id: UUID) -> List[PaymentModel]:
        """Get all payments for a ticket.
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            List of payments
        """
        return self.db.query(self.model).filter(
            self.model.ticket_id == ticket_id
        ).order_by(self.model.created_at.desc()).all()
    
    def get_completed_payments(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PaymentModel]:
        """Get completed payments within date range.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of completed payments
        """
        query = self.db.query(self.model).filter(
            self.model.payment_status == PaymentStatus.COMPLETED
        )
        
        if start_date:
            query = query.filter(self.model.paid_at >= start_date)
        if end_date:
            query = query.filter(self.model.paid_at <= end_date)
        
        return query.order_by(
            self.model.paid_at.desc()
        ).offset(skip).limit(limit).all()
