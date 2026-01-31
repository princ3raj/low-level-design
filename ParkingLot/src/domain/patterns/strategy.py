"""Strategy pattern for pricing calculations."""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from src.domain.enums import SpotType


class PricingStrategy(ABC):
    """Abstract base class for pricing strategies."""
    
    @abstractmethod
    def calculate_price(
        self,
        duration_hours: float,
        spot_type: SpotType,
        base_rate: Decimal,
        hourly_rate: Decimal
    ) -> Decimal:
        """Calculate parking price.
        
        Args:
            duration_hours: Parking duration in hours
            spot_type: Type of parking spot
            base_rate: Base parking fee
            hourly_rate: Hourly rate
            
        Returns:
            Total parking charge
        """
        pass


class HourlyPricingStrategy(PricingStrategy):
    """Standard hourly pricing strategy.
    
    Formula: base_rate + (hourly_rate * hours)
    """
    
    def __init__(self, daily_max: Optional[Decimal] = None):
        """Initialize hourly pricing strategy.
        
        Args:
            daily_max: Optional maximum daily charge
        """
        self.daily_max = daily_max
    
    def calculate_price(
        self,
        duration_hours: float,
        spot_type: SpotType,
        base_rate: Decimal,
        hourly_rate: Decimal
    ) -> Decimal:
        """Calculate hourly price."""
        # Base + hourly charges
        price = base_rate + (Decimal(str(duration_hours)) * hourly_rate)
        
        # Apply daily maximum if set
        if self.daily_max and price > self.daily_max:
            price = self.daily_max
        
        return price.quantize(Decimal('0.01'))


class DynamicPricingStrategy(PricingStrategy):
    """Dynamic pricing based on demand/occupancy.
    
    Applies a multiplier when occupancy exceeds threshold.
    """
    
    def __init__(
        self,
        occupancy_rate: float,
        threshold: float = 0.9,
        multiplier: Decimal = Decimal('1.5'),
        daily_max: Optional[Decimal] = None
    ):
        """Initialize dynamic pricing strategy.
        
        Args:
            occupancy_rate: Current occupancy rate (0.0 to 1.0)
            threshold: Occupancy threshold to trigger higher pricing
            multiplier: Price multiplier when above threshold
            daily_max: Optional maximum daily charge
        """
        self.occupancy_rate = occupancy_rate
        self.threshold = threshold
        self.multiplier = multiplier
        self.daily_max = daily_max
        self.base_strategy = HourlyPricingStrategy(daily_max)
    
    def calculate_price(
        self,
        duration_hours: float,
        spot_type: SpotType,
        base_rate: Decimal,
        hourly_rate: Decimal
    ) -> Decimal:
        """Calculate dynamic price based on occupancy."""
        # Calculate base price using hourly strategy
        base_price = self.base_strategy.calculate_price(
            duration_hours, spot_type, base_rate, hourly_rate
        )
        
        # Apply demand multiplier if occupancy is high
        if self.occupancy_rate >= self.threshold:
            base_price = base_price * self.multiplier
        
        # Apply daily maximum if set
        if self.daily_max and base_price > self.daily_max:
            base_price = self.daily_max
        
        return base_price.quantize(Decimal('0.01'))


class ReservedPricingStrategy(PricingStrategy):
    """Fixed pricing for reserved/monthly parking."""
    
    def __init__(self, fixed_amount: Decimal):
        """Initialize reserved pricing strategy.
        
        Args:
            fixed_amount: Fixed monthly/annual amount
        """
        self.fixed_amount = fixed_amount
    
    def calculate_price(
        self,
        duration_hours: float,
        spot_type: SpotType,
        base_rate: Decimal,
        hourly_rate: Decimal
    ) -> Decimal:
        """Return fixed price regardless of duration."""
        return self.fixed_amount.quantize(Decimal('0.01'))


class ValetPricingStrategy(PricingStrategy):
    """Pricing with additional valet service charge."""
    
    def __init__(
        self,
        valet_charge: Decimal,
        daily_max: Optional[Decimal] = None
    ):
        """Initialize valet pricing strategy.
        
        Args:
            valet_charge: Additional charge for valet service
            daily_max: Optional maximum daily charge
        """
        self.valet_charge = valet_charge
        self.base_strategy = HourlyPricingStrategy(daily_max)
    
    def calculate_price(
        self,
        duration_hours: float,
        spot_type: SpotType,
        base_rate: Decimal,
        hourly_rate: Decimal
    ) -> Decimal:
        """Calculate price with valet charge."""
        base_price = self.base_strategy.calculate_price(
            duration_hours, spot_type, base_rate, hourly_rate
        )
        return (base_price + self.valet_charge).quantize(Decimal('0.01'))


class EVChargingPricingStrategy(PricingStrategy):
    """Pricing with additional EV charging fee."""
    
    def __init__(
        self,
        charging_rate_per_hour: Decimal,
        daily_max: Optional[Decimal] = None
    ):
        """Initialize EV charging pricing strategy.
        
        Args:
            charging_rate_per_hour: Additional hourly rate for charging
            daily_max: Optional maximum daily charge
        """
        self.charging_rate_per_hour = charging_rate_per_hour
        self.base_strategy = HourlyPricingStrategy(daily_max)
    
    def calculate_price(
        self,
        duration_hours: float,
        spot_type: SpotType,
        base_rate: Decimal,
        hourly_rate: Decimal
    ) -> Decimal:
        """Calculate price with charging fee."""
        base_price = self.base_strategy.calculate_price(
            duration_hours, spot_type, base_rate, hourly_rate
        )
        
        # Add charging fee if it's an electric spot
        if spot_type == SpotType.ELECTRIC:
            charging_fee = Decimal(str(duration_hours)) * self.charging_rate_per_hour
            base_price += charging_fee
        
        return base_price.quantize(Decimal('0.01'))
