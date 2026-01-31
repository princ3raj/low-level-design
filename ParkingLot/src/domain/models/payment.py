"""Payment domain model."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.domain.base_entity import BaseEntity
from src.domain.enums import PaymentMethod, PaymentStatus


class Payment(BaseEntity):
    """Payment entity representing a payment transaction."""
    
    def __init__(
        self,
        ticket_id: UUID,
        amount: Decimal,
        payment_method: PaymentMethod,
        idempotency_key: str,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
        transaction_id: Optional[str] = None,
        paid_at: Optional[datetime] = None,
        id: Optional[UUID] = None
    ):
        """Initialize payment.
        
        Args:
            ticket_id: ID of associated ticket
            amount: Payment amount
            payment_method: Method of payment
            idempotency_key: Unique key for idempotent processing
            payment_status: Current payment status
            transaction_id: External transaction ID
            paid_at: Timestamp of payment completion
            id: Optional UUID identifier
        """
        super().__init__(id)
        self.ticket_id = ticket_id
        self.amount = amount
        self.payment_method = payment_method
        self.idempotency_key = idempotency_key
        self.payment_status = payment_status
        self.transaction_id = transaction_id
        self.paid_at = paid_at
    
    def is_completed(self) -> bool:
        """Check if payment is completed.
        
        Returns:
            True if payment is completed, False otherwise
        """
        return self.payment_status == PaymentStatus.COMPLETED
    
    def is_pending(self) -> bool:
        """Check if payment is pending.
        
        Returns:
            True if payment is pending, False otherwise
        """
        return self.payment_status == PaymentStatus.PENDING
    
    def mark_as_completed(self, transaction_id: str) -> None:
        """Mark payment as completed.
        
        Args:
            transaction_id: Transaction identifier from payment gateway
            
        Raises:
            ValueError: If payment is not pending
        """
        if not self.is_pending():
            raise ValueError(f"Payment {self.id} is not pending")
        
        self.payment_status = PaymentStatus.COMPLETED
        self.transaction_id = transaction_id
        self.paid_at = datetime.utcnow()
        self.update_timestamp()
    
    def mark_as_failed(self) -> None:
        """Mark payment as failed."""
        self.payment_status = PaymentStatus.FAILED
        self.update_timestamp()
    
    def refund(self) -> None:
        """Mark payment as refunded.
        
        Raises:
            ValueError: If payment is not completed
        """
        if not self.is_completed():
            raise ValueError(f"Payment {self.id} is not completed, cannot refund")
        
        self.payment_status = PaymentStatus.REFUNDED
        self.update_timestamp()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Payment(id={self.id}, amount={self.amount}, "
            f"status={self.payment_status.value}, method={self.payment_method.value})"
        )
