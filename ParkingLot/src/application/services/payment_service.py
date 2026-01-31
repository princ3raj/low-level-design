"""Payment service for processing payments."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.domain.enums import PaymentMethod, PaymentStatus, TicketStatus
from src.infrastructure.database.models import PaymentModel
from src.infrastructure.repository.ticket_repository import PaymentRepository, TicketRepository


class PaymentService:
    """Service for processing parking payments."""
    
    def __init__(self, db: Session):
        """Initialize payment service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.ticket_repo = TicketRepository(db)
    
    def process_payment(
        self,
        ticket_id: UUID,
        amount: Decimal,
        payment_method: PaymentMethod,
        idempotency_key: str,
        coupon_code: Optional[str] = None
    ) -> PaymentModel:
        """Process payment with idempotency.
        
        Args:
            ticket_id: Ticket ID
            amount: Payment amount
            payment_method: Payment method
            idempotency_key: Unique key for idempotent processing
            coupon_code: Optional coupon code
            
        Returns:
            PaymentModel
            
        Raises:
            ValueError: If ticket not found or already paid
        """
        # Check for existing payment with same idempotency key
        existing_payment = self.payment_repo.get_by_idempotency_key(idempotency_key)
        if existing_payment:
            # Return existing payment (idempotent behavior)
            return existing_payment
        
        # Get ticket
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        if ticket.status == TicketStatus.PAID:
            raise ValueError(f"Ticket {ticket_id} already paid")
        
        # Create payment
        payment = PaymentModel(
            ticket_id=ticket_id,
            amount=amount,
            payment_method=payment_method,
            idempotency_key=idempotency_key,
            payment_status=PaymentStatus.PENDING
        )
        payment = self.payment_repo.create(payment)
        
        try:
            # Simulate payment processing
            # In production, this would call payment gateway
            transaction_id = f"TXN-{uuid4().hex[:12].upper()}"
            
            # Mark payment as completed
            payment.payment_status = PaymentStatus.COMPLETED
            payment.transaction_id = transaction_id
            payment.paid_at = datetime.utcnow()
            
            # Mark ticket as paid
            ticket.status = TicketStatus.PAID
            
            self.db.commit()
            return payment
            
        except Exception as e:
            # Mark payment as failed
            payment.payment_status = PaymentStatus.FAILED
            self.db.commit()
            raise ValueError(f"Payment processing failed: {str(e)}")
    
    def get_payment(self, payment_id: UUID) -> Optional[PaymentModel]:
        """Get payment by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            PaymentModel or None
        """
        return self.payment_repo.get_by_id(payment_id)
    
    def refund_payment(self, payment_id: UUID) -> PaymentModel:
        """Refund a payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Updated PaymentModel
            
        Raises:
            ValueError: If payment not found or cannot be refunded
        """
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.payment_status != PaymentStatus.COMPLETED:
            raise ValueError("Can only refund completed payments")
        
        # Process refund
        payment.payment_status = PaymentStatus.REFUNDED
        
        # Update ticket status
        ticket = self.ticket_repo.get_by_id(payment.ticket_id)
        if ticket:
            ticket.status = TicketStatus.CANCELLED
        
        self.db.commit()
        return payment
