"""Payment repository"""
from typing import List, Optional
from .base_repository import BaseRepository
from ..domain.models.payment import Payment
from ..domain.enums.order_status import PaymentStatus


class PaymentRepository(BaseRepository[Payment]):
    """Repository for payment entities"""
    
    def _get_entity_id(self, entity: Payment) -> str:
        return entity.id
    
    def find_by_order(self, order_id: str) -> Optional[Payment]:
        """Find payment by order ID"""
        for payment in self._storage.values():
            if payment.order_id == order_id:
                return payment
        return None
    
    def find_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Find payment by transaction ID"""
        for payment in self._storage.values():
            if payment.transaction_id == transaction_id:
                return payment
        return None
    
    def find_by_idempotency_key(self, idempotency_key: str) -> Optional[Payment]:
        """
        Find payment by idempotency key
        Used to prevent duplicate payment processing
        """
        for payment in self._storage.values():
            if payment.idempotency_key == idempotency_key:
                return payment
        return None
    
    def find_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Find payments by status"""
        return [
            p for p in self._storage.values()
            if p.status == status
        ]
    
    def find_pending_payments(self) -> List[Payment]:
        """Find all pending payments"""
        return self.find_by_status(PaymentStatus.PENDING)
    
    def find_failed_payments(self) -> List[Payment]:
        """Find all failed payments"""
        return self.find_by_status(PaymentStatus.FAILED)
