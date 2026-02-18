"""Payment processing service with factory pattern"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4
from ..domain.models.payment import Payment
from ..domain.enums.order_status import PaymentMethod, PaymentStatus
from ..domain.value_objects import Money
from ..domain.exceptions import PaymentFailed
from ..repositories.payment_repository import PaymentRepository


class PaymentGateway(ABC):
    """Abstract payment gateway"""
    
    @abstractmethod
    def process_payment(self, amount: Money, **kwargs) -> tuple[bool, str]:
        """
        Process payment through gateway
        Returns (success: bool, transaction_id: str)
        """
        pass
    
    @abstractmethod
    def process_refund(self, transaction_id: str, amount: Money) -> bool:
        """Process refund through gateway"""
        pass


class CashPaymentGateway(PaymentGateway):
    """Cash on delivery payment"""
    
    def process_payment(self, amount: Money, **kwargs) -> tuple[bool, str]:
        """Cash payments are always successful (collected on delivery)"""
        transaction_id = f"CASH-{uuid4().hex[:8]}"
        return True, transaction_id
    
    def process_refund(self, transaction_id: str, amount: Money) -> bool:
        """Cash refunds handled manually"""
        return True


class CardPaymentGateway(PaymentGateway):
    """Credit/Debit card payment gateway (mock)"""
    
    def process_payment(self, amount: Money, **kwargs) -> tuple[bool, str]:
        """Simulate card payment processing"""
        # In real implementation, this would call external gateway API
        transaction_id = f"CARD-{uuid4().hex[:8]}"
        return True, transaction_id
    
    def process_refund(self, transaction_id: str, amount: Money) -> bool:
        """Simulate card refund"""
        return True


class UPIPaymentGateway(PaymentGateway):
    """UPI payment gateway (mock)"""
    
    def process_payment(self, amount: Money, **kwargs) -> tuple[bool, str]:
        """Simulate UPI payment processing"""
        transaction_id = f"UPI-{uuid4().hex[:8]}"
        return True, transaction_id
    
    def process_refund(self, transaction_id: str, amount: Money) -> bool:
        """Simulate UPI refund"""
        return True


class PaymentGatewayFactory:
    """Factory for creating payment gateways"""
    
    @staticmethod
    def create_gateway(payment_method: PaymentMethod) -> PaymentGateway:
        """Create appropriate payment gateway based on method"""
        gateways = {
            PaymentMethod.CASH: CashPaymentGateway,
            PaymentMethod.CARD: CardPaymentGateway,
            PaymentMethod.UPI: UPIPaymentGateway,
            PaymentMethod.WALLET: CardPaymentGateway  # Similar to card
        }
        
        gateway_class = gateways.get(payment_method)
        if not gateway_class:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        return gateway_class()


class PaymentService:
    """Service for payment processing"""
    
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo
    
    def create_payment(self, order_id: str, amount: Money,
                       payment_method: PaymentMethod,
                       idempotency_key: Optional[str] = None) -> Payment:
        """
        Create and process a payment with idempotency support
        """
        # Check idempotency key to prevent duplicate payments
        if idempotency_key:
            existing_payment = self.payment_repo.find_by_idempotency_key(
                idempotency_key
            )
            if existing_payment:
                return existing_payment
        
        # Check if payment already exists for order
        existing_payment = self.payment_repo.find_by_order(order_id)
        if existing_payment and existing_payment.is_successful():
            return existing_payment
        
        # Create payment
        payment = Payment(
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            idempotency_key=idempotency_key or str(uuid4())
        )
        
        self.payment_repo.save(payment)
        
        # Process payment
        return self.process_payment(payment.id)
    
    def process_payment(self, payment_id: str) -> Payment:
        """Process a payment"""
        payment = self.payment_repo.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.is_successful():
            return payment
        
        payment.mark_processing()
        self.payment_repo.save(payment)
        
        try:
            # Get appropriate gateway
            gateway = PaymentGatewayFactory.create_gateway(payment.payment_method)
            
            # Process payment
            success, transaction_id = gateway.process_payment(payment.amount)
            
            if success:
                payment.mark_completed(transaction_id)
            else:
                payment.mark_failed("Gateway declined payment")
        
        except Exception as e:
            payment.mark_failed(str(e))
        
        self.payment_repo.save(payment)
        
        if not payment.is_successful():
            raise PaymentFailed(payment.failure_reason or "Unknown error")
        
        return payment
    
    def refund_payment(self, payment_id: str, amount: Optional[Money] = None) -> Payment:
        """Process refund for a payment"""
        payment = self.payment_repo.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if not payment.is_successful():
            raise ValueError("Cannot refund unsuccessful payment")
        
        # Default to full refund
        refund_amount = amount or payment.amount
        
        try:
            gateway = PaymentGatewayFactory.create_gateway(payment.payment_method)
            
            if gateway.process_refund(payment.transaction_id, refund_amount):
                payment.process_refund(refund_amount)
                self.payment_repo.save(payment)
            else:
                raise PaymentFailed("Refund processing failed")
        
        except Exception as e:
            raise PaymentFailed(f"Refund failed: {str(e)}")
        
        return payment
    
    def get_payment_by_order(self, order_id: str) -> Optional[Payment]:
        """Get payment for an order"""
        return self.payment_repo.find_by_order(order_id)
