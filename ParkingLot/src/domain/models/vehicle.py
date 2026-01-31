"""Vehicle domain model."""
import re
from typing import Optional
from uuid import UUID

from src.domain.base_entity import BaseEntity
from src.domain.enums import VehicleType


class Vehicle(BaseEntity):
    """Vehicle entity representing a vehicle in the parking system."""
    
    # License plate validation pattern (alphanumeric, 3-20 chars)
    LICENSE_PLATE_PATTERN = re.compile(r'^[A-Z0-9]{3,20}$')
    
    def __init__(
        self,
        license_plate: str,
        vehicle_type: VehicleType,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
        id: Optional[UUID] = None
    ):
        """Initialize Vehicle entity.
        
        Args:
            license_plate: Unique license plate number
            vehicle_type: Type of vehicle
            owner_name: Name of vehicle owner
            owner_phone: Phone number of owner
            id: Optional UUID identifier
            
        Raises:
            ValueError: If license plate is invalid
        """
        super().__init__(id)
        self.license_plate = self._validate_license_plate(license_plate)
        self.vehicle_type = vehicle_type
        self.owner_name = owner_name
        self.owner_phone = owner_phone
    
    def _validate_license_plate(self, license_plate: str) -> str:
        """Validate and normalize license plate.
        
        Args:
            license_plate: License plate to validate
            
        Returns:
            Normalized license plate (uppercase, no spaces)
            
        Raises:
            ValueError: If license plate format is invalid
        """
        # Normalize: uppercase and remove spaces
        normalized = license_plate.upper().replace(" ", "")
        
        if not self.LICENSE_PLATE_PATTERN.match(normalized):
            raise ValueError(
                f"Invalid license plate format: {license_plate}. "
                "Must be 3-20 alphanumeric characters."
            )
        
        return normalized
    
    def is_electric(self) -> bool:
        """Check if vehicle is electric.
        
        Returns:
            True if vehicle is electric, False otherwise
        """
        return self.vehicle_type == VehicleType.ELECTRIC_CAR
    
    def get_compatible_spot_types(self) -> list:
        """Get list of compatible spot types for this vehicle.
        
        Returns:
            List of SpotType enums compatible with this vehicle
        """
        from src.domain.enums import SpotType
        
        compatible_spots = []
        
        if self.vehicle_type == VehicleType.MOTORCYCLE:
            compatible_spots = [SpotType.MOTORCYCLE, SpotType.COMPACT]
        elif self.vehicle_type in [VehicleType.CAR, VehicleType.ELECTRIC_CAR]:
            compatible_spots = [SpotType.COMPACT, SpotType.LARGE, SpotType.HANDICAPPED]
            if self.is_electric():
                compatible_spots.append(SpotType.ELECTRIC)
        elif self.vehicle_type in [VehicleType.TRUCK, VehicleType.VAN]:
            compatible_spots = [SpotType.LARGE]
        
        return compatible_spots
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Vehicle(id={self.id}, license_plate={self.license_plate}, "
            f"type={self.vehicle_type.value})"
        )
