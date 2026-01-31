"""Factory pattern for creating parking spots."""
from typing import Optional
from uuid import UUID

from src.domain.enums import SpotType, SpotStatus
from src.domain.models.parking_lot import ParkingSpot


class SpotFactory:
    """Factory for creating different types of parking spots.
    
    This factory encapsulates the logic for creating parking spots
    with appropriate configurations based on spot type.
    """
    
    @staticmethod
    def create_spot(
        spot_number: str,
        spot_type: SpotType,
        floor_id: UUID,
        id: Optional[UUID] = None
    ) -> ParkingSpot:
        """Create a parking spot with appropriate configuration.
        
        Args:
            spot_number: Spot identifier
            spot_type: Type of spot to create
            floor_id: ID of the floor
            id: Optional UUID for the spot
            
        Returns:
            Configured ParkingSpot instance
        """
        # Electric spots have charging enabled by default
        is_charging = spot_type == SpotType.ELECTRIC
        
        return ParkingSpot(
            spot_number=spot_number,
            spot_type=spot_type,
            floor_id=floor_id,
            status=SpotStatus.AVAILABLE,
            is_charging_enabled=is_charging,
            id=id
        )
    
    @staticmethod
    def create_compact_spot(
        spot_number: str,
        floor_id: UUID,
        id: Optional[UUID] = None
    ) -> ParkingSpot:
        """Create a compact parking spot."""
        return SpotFactory.create_spot(spot_number, SpotType.COMPACT, floor_id, id)
    
    @staticmethod
    def create_large_spot(
        spot_number: str,
        floor_id: UUID,
        id: Optional[UUID] = None
    ) -> ParkingSpot:
        """Create a large parking spot."""
        return SpotFactory.create_spot(spot_number, SpotType.LARGE, floor_id, id)
    
    @staticmethod
    def create_handicapped_spot(
        spot_number: str,
        floor_id: UUID,
        id: Optional[UUID] = None
    ) -> ParkingSpot:
        """Create a handicapped parking spot."""
        return SpotFactory.create_spot(spot_number, SpotType.HANDICAPPED, floor_id, id)
    
    @staticmethod
    def create_motorcycle_spot(
        spot_number: str,
        floor_id: UUID,
        id: Optional[UUID] = None
    ) -> ParkingSpot:
        """Create a motorcycle parking spot."""
        return SpotFactory.create_spot(spot_number, SpotType.MOTORCYCLE, floor_id, id)
    
    @staticmethod
    def create_electric_spot(
        spot_number: str,
        floor_id: UUID,
        id: Optional[UUID] = None
    ) -> ParkingSpot:
        """Create an electric vehicle parking spot with charging."""
        return SpotFactory.create_spot(spot_number, SpotType.ELECTRIC, floor_id, id)
