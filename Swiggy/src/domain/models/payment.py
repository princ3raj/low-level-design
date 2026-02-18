"""Payment domain model"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from ..enums.order_status import PaymentStatus, PaymentMethod
from ..value_objects import Money


@dataclass
class Payment:
    """Payment entity"""
    id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    amount: Money = field(default_factory=lambda: Money(0.0))
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: PaymentMethod = PaymentMethod.CASH
    transaction_id: Optional[str] = None
    idempotency_key: Optional[str] = None  # For preventing duplicate payments
    gateway_response: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    refund_amount: Money = field(default_factory=lambda: Money(0.0))
    
    def mark_processing(self):
        """Mark payment as processing"""
        self.status = PaymentStatus.PROCESSING
    
    def mark_completed(self, transaction_id: str):
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED
        self.transaction_id = transaction_id
        self.completed_at = datetime.now()
    
    def mark_failed(self, reason: str):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.failed_at = datetime.now()
    
    def process_refund(self, amount: Money):
        """Process refund for the payment"""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Cannot refund a payment that is not completed")
        
        if amount.amount > self.amount.amount:
            raise ValueError("Refund amount cannot exceed payment amount")
        
        self.status = PaymentStatus.REFUNDED
        self.refund_amount = amount
        self.refunded_at = datetime.now()
    
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == PaymentStatus.COMPLETED
