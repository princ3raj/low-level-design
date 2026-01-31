"""Payment processing endpoints."""
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import PaymentRequest, PaymentResponse
from src.application.services.parking_service import ParkingService
from src.application.services.payment_service import PaymentService
from src.infrastructure.database.connection import get_db

router = APIRouter()


@router.post("/payments", response_model=PaymentResponse, status_code=201)
def process_payment(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db)
):
    """Process parking payment.
    
    This endpoint supports idempotent payment processing using the idempotency_key.
    If a payment with the same idempotency_key exists, it returns that payment instead
    of creating a new one.
    
    Args:
        payment_data: Payment request data
        db: Database session
        
    Returns:
        Payment response
    """
    payment_service = PaymentService(db)
    parking_service = ParkingService(db)
    
    try:
        # Process payment
        payment = payment_service.process_payment(
            ticket_id=payment_data.ticket_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            idempotency_key=payment_data.idempotency_key,
            coupon_code=payment_data.coupon_code
        )
        
        # Complete exit process (vacate spot)
        if payment.payment_status.value == "COMPLETED":
            parking_service.complete_exit(payment.ticket_id)
        
        # Calculate final amount after discount
        discount = Decimal('0.00')
        if payment_data.coupon_code:
            # In production, get discount from coupon service
            discount = payment.amount * Decimal('0.10')
        
        final_amount = payment.amount - discount
        
        return PaymentResponse(
            payment_id=payment.id,
            ticket_id=payment.ticket_id,
            amount=payment.amount,
            discount=discount,
            final_amount=final_amount,
            payment_status=payment.payment_status,
            payment_method=payment.payment_method,
            transaction_id=payment.transaction_id,
            paid_at=payment.paid_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get payment details.
    
    Args:
        payment_id: Payment ID
        db: Database session
        
    Returns:
        Payment details
    """
    payment_service = PaymentService(db)
    payment = payment_service.get_payment(payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return PaymentResponse(
        payment_id=payment.id,
        ticket_id=payment.ticket_id,
        amount=payment.amount,
        discount=Decimal('0.00'),
        final_amount=payment.amount,
        payment_status=payment.payment_status,
        payment_method=payment.payment_method,
        transaction_id=payment.transaction_id,
        paid_at=payment.paid_at
    )
