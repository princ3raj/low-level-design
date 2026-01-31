"""Pricing service for calculating parking charges."""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.enums import SpotType
from src.domain.patterns.strategy import (
    DynamicPricingStrategy,
    EVChargingPricingStrategy,
    HourlyPricingStrategy,
    PricingStrategy,
    ValetPricingStrategy,
)
from src.infrastructure.repository.parking_repository import (
    ParkingLotRepository,
    ParkingSpotRepository,
)


class PricingService:
    """Service for calculating parking charges."""
    
    def __init__(self, db: Session):
        """Initialize pricing service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.lot_repo = ParkingLotRepository(db)
        self.spot_repo = ParkingSpotRepository(db)
    
    def calculate_charges(
        self,
        parking_lot_id: UUID,
        spot_id: UUID,
        duration_hours: float,
        is_valet: bool = False,
        is_ev_charging: bool = False
    ) -> dict:
        """Calculate parking charges.
        
        Args:
            parking_lot_id: Parking lot ID
            spot_id: Parking spot ID
            duration_hours: Parking duration in hours
            is_valet: Whether valet service was used
            is_ev_charging: Whether EV charging was used
            
        Returns:
            Dictionary with charge breakdown
        """
        # Get spot details
        spot = self.spot_repo.get_by_id(spot_id)
        if not spot:
            raise ValueError(f"Spot {spot_id} not found")
        
        # Default pricing (should be loaded from pricing_rules table in production)
        base_rate = Decimal('5.00')
        hourly_rate = Decimal('5.00')
        daily_max = Decimal('100.00')
        
        # Choose pricing strategy based on conditions
        strategy = self._get_pricing_strategy(
            parking_lot_id=parking_lot_id,
            spot_type=spot.spot_type,
            is_valet=is_valet,
            is_ev_charging=is_ev_charging
        )
        
        # Calculate price
        total_price = strategy.calculate_price(
            duration_hours=duration_hours,
            spot_type=spot.spot_type,
            base_rate=base_rate,
            hourly_rate=hourly_rate
        )
        
        # Build charge breakdown
        charges = {
            'base_charge': float(base_rate),
            'hourly_charge': float(Decimal(str(duration_hours)) * hourly_rate),
            'valet_charge': 0.0,
            'charging_fee': 0.0,
            'subtotal': float(total_price),
            'discount': 0.0,
            'total': float(total_price)
        }
        
        # Add valet charge if applicable
        if is_valet:
            valet_charge = Decimal('10.00')
            charges['valet_charge'] = float(valet_charge)
            charges['total'] += float(valet_charge)
        
        # Add EV charging fee if applicable
        if is_ev_charging and spot.spot_type == SpotType.ELECTRIC:
            charging_fee = Decimal('2.00') * Decimal(str(duration_hours))
            charges['charging_fee'] = float(charging_fee)
            charges['total'] += float(charging_fee)
        
        return charges
    
    def _get_pricing_strategy(
        self,
        parking_lot_id: UUID,
        spot_type: SpotType,
        is_valet: bool,
        is_ev_charging: bool
    ) -> PricingStrategy:
        """Get appropriate pricing strategy.
        
        Args:
            parking_lot_id: Parking lot ID
            spot_type: Type of spot
            is_valet: Whether valet service
            is_ev_charging: Whether EV charging
            
        Returns:
            PricingStrategy instance
        """
        daily_max = Decimal('100.00')
        
        # Calculate occupancy rate for dynamic pricing
        stats = self.spot_repo.get_availability_stats(parking_lot_id)
        total_spots = sum(s['total'] for s in stats.values())
        available_spots = sum(s['available'] for s in stats.values())
        occupancy_rate = 1.0 - (available_spots / total_spots) if total_spots > 0 else 0.0
        
        # Choose strategy based on conditions
        if is_ev_charging and spot_type == SpotType.ELECTRIC:
            return EVChargingPricingStrategy(
                charging_rate_per_hour=Decimal('2.00'),
                daily_max=daily_max
            )
        elif is_valet:
            return ValetPricingStrategy(
                valet_charge=Decimal('10.00'),
                daily_max=daily_max
            )
        elif occupancy_rate >= 0.9:  # High demand
            return DynamicPricingStrategy(
                occupancy_rate=occupancy_rate,
                threshold=0.9,
                multiplier=Decimal('1.5'),
                daily_max=daily_max
            )
        else:
            return HourlyPricingStrategy(daily_max=daily_max)
    
    def apply_discount(
        self,
        original_amount: Decimal,
        coupon_code: Optional[str] = None
    ) -> Tuple[Decimal, Decimal]:
        """Apply discount to amount.
        
        Args:
            original_amount: Original charge amount
            coupon_code: Optional coupon code
            
        Returns:
            Tuple of (discount_amount, final_amount)
        """
        if not coupon_code:
            return Decimal('0.00'), original_amount
        
        # In production, this would validate coupon from database
        # For now, simple example: 10% discount
        discount = original_amount * Decimal('0.10')
        final_amount = original_amount - discount
        
        return discount, final_amount


from typing import Tuple
