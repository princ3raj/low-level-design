"""Parking lot domain models."""
from typing import List, Optional
from uuid import UUID

from src.domain.base_entity import BaseEntity
from src.domain.enums import SpotType, SpotStatus


class ParkingSpot(BaseEntity):
    """Parking spot entity."""
    
    def __init__(
        self,
        spot_number: str,
        spot_type: SpotType,
        floor_id: UUID,
        status: SpotStatus = SpotStatus.AVAILABLE,
        is_charging_enabled: bool = False,
        version: int = 0,
        id: Optional[UUID] = None
    ):
        """Initialize parking spot.
        
        Args:
            spot_number: Spot identifier (e.g., "A1", "B12")
            spot_type: Type of spot
            floor_id: ID of the floor this spot belongs to
            status: Current status of the spot
            is_charging_enabled: Whether EV charging is available
            version: Version for optimistic locking
            id: Optional UUID identifier
        """
        super().__init__(id)
        self.spot_number = spot_number
        self.spot_type = spot_type
        self.floor_id = floor_id
        self.status = status
        self.is_charging_enabled = is_charging_enabled
        self.version = version
    
    def is_available(self) -> bool:
        """Check if spot is available for parking.
        
        Returns:
            True if spot is available, False otherwise
        """
        return self.status == SpotStatus.AVAILABLE
    
    def can_accommodate(self, vehicle_spot_types: List[SpotType]) -> bool:
        """Check if this spot can accommodate a vehicle.
        
        Args:
            vehicle_spot_types: List of compatible spot types for vehicle
            
        Returns:
            True if spot is available and compatible
        """
        return self.is_available() and self.spot_type in vehicle_spot_types
    
    def occupy(self) -> None:
        """Mark spot as occupied.
        
        Raises:
            ValueError: If spot is not available
        """
        if not self.is_available():
            raise ValueError(f"Spot {self.spot_number} is not available")
        self.status = SpotStatus.OCCUPIED
        self.update_timestamp()
    
    def vacate(self) -> None:
        """Mark spot as available.
        
        Raises:
            ValueError: If spot is not occupied
        """
        if self.status != SpotStatus.OCCUPIED:
            raise ValueError(f"Spot {self.spot_number} is not occupied")
        self.status = SpotStatus.AVAILABLE
        self.update_timestamp()
    
    def reserve(self) -> None:
        """Mark spot as reserved."""
        if not self.is_available():
            raise ValueError(f"Spot {self.spot_number} is not available")
        self.status = SpotStatus.RESERVED
        self.update_timestamp()
    
    def mark_out_of_service(self) -> None:
        """Mark spot as out of service."""
        self.status = SpotStatus.OUT_OF_SERVICE
        self.update_timestamp()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ParkingSpot(number={self.spot_number}, type={self.spot_type.value}, "
            f"status={self.status.value})"
        )


class Floor(BaseEntity):
    """Floor entity containing multiple parking spots."""
    
    def __init__(
        self,
        floor_number: int,
        parking_lot_id: UUID,
        spots: Optional[List[ParkingSpot]] = None,
        id: Optional[UUID] = None
    ):
        """Initialize floor.
        
        Args:
            floor_number: Floor number (1-indexed)
            parking_lot_id: ID of the parking lot
            spots: List of parking spots on this floor
            id: Optional UUID identifier
        """
        super().__init__(id)
        self.floor_number = floor_number
        self.parking_lot_id = parking_lot_id
        self.spots: List[ParkingSpot] = spots or []
    
    def add_spot(self, spot: ParkingSpot) -> None:
        """Add a parking spot to this floor.
        
        Args:
            spot: Parking spot to add
        """
        self.spots.append(spot)
        self.update_timestamp()
    
    def get_available_spots(self, spot_type: Optional[SpotType] = None) -> List[ParkingSpot]:
        """Get all available spots, optionally filtered by type.
        
        Args:
            spot_type: Optional spot type to filter by
            
        Returns:
            List of available parking spots
        """
        available = [spot for spot in self.spots if spot.is_available()]
        if spot_type:
            available = [spot for spot in available if spot.spot_type == spot_type]
        return available
    
    def get_total_spots(self) -> int:
        """Get total number of spots on this floor."""
        return len(self.spots)
    
    def get_available_count(self) -> int:
        """Get count of available spots."""
        return len([spot for spot in self.spots if spot.is_available()])
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Floor(number={self.floor_number}, total_spots={self.get_total_spots()}, "
            f"available={self.get_available_count()})"
        )


class ParkingLot(BaseEntity):
    """Parking lot entity containing multiple floors."""
    
    def __init__(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        floors: Optional[List[Floor]] = None,
        id: Optional[UUID] = None
    ):
        """Initialize parking lot.
        
        Args:
            name: Name of the parking lot
            address: Street address
            city: City
            state: State
            zip_code: ZIP code
            floors: List of floors
            id: Optional UUID identifier
        """
        super().__init__(id)
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.floors: List[Floor] = floors or []
    
    def add_floor(self, floor: Floor) -> None:
        """Add a floor to the parking lot.
        
        Args:
            floor: Floor to add
        """
        self.floors.append(floor)
        self.update_timestamp()
    
    def get_total_floors(self) -> int:
        """Get total number of floors."""
        return len(self.floors)
    
    def get_total_spots(self) -> int:
        """Get total number of parking spots across all floors."""
        return sum(floor.get_total_spots() for floor in self.floors)
    
    def get_available_spots_count(self) -> int:
        """Get total count of available spots."""
        return sum(floor.get_available_count() for floor in self.floors)
    
    def find_available_spot(
        self,
        vehicle_spot_types: List[SpotType],
        preferred_spot_type: Optional[SpotType] = None
    ) -> Optional[ParkingSpot]:
        """Find an available spot for a vehicle.
        
        Args:
            vehicle_spot_types: List of compatible spot types
            preferred_spot_type: Preferred spot type if available
            
        Returns:
            Available parking spot or None if no spots available
        """
        # Try to find preferred spot type first
        if preferred_spot_type and preferred_spot_type in vehicle_spot_types:
            for floor in self.floors:
                for spot in floor.spots:
                    if spot.spot_type == preferred_spot_type and spot.is_available():
                        return spot
        
        # Find any compatible spot
        for floor in self.floors:
            for spot in floor.spots:
                if spot.can_accommodate(vehicle_spot_types):
                    return spot
        
        return None
    
    def get_availability_by_type(self) -> dict:
        """Get availability statistics grouped by spot type.
        
        Returns:
            Dictionary with spot type as key and availability stats as value
        """
        stats = {}
        for spot_type in SpotType:
            total = 0
            available = 0
            for floor in self.floors:
                floor_spots = [s for s in floor.spots if s.spot_type == spot_type]
                total += len(floor_spots)
                available += len([s for s in floor_spots if s.is_available()])
            
            if total > 0:
                stats[spot_type.value] = {
                    "total": total,
                    "available": available,
                    "occupied": total - available
                }
        
        return stats
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ParkingLot(name={self.name}, floors={self.get_total_floors()}, "
            f"spots={self.get_total_spots()}, available={self.get_available_spots_count()})"
        )
