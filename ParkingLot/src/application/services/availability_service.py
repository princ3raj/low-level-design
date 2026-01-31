"""Availability service for real-time parking availability."""
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.enums import SpotType
from src.domain.patterns.observer import Subject
from src.infrastructure.repository.parking_repository import (
    ParkingLotRepository,
    ParkingSpotRepository,
)


class AvailabilityService(Subject):
    """Service for querying parking availability."""
    
    def __init__(self, db: Session):
        """Initialize availability service.
        
        Args:
            db: Database session
        """
        super().__init__()
        self.db = db
        self.lot_repo = ParkingLotRepository(db)
        self.spot_repo = ParkingSpotRepository(db)
    
    def get_availability(self, parking_lot_id: UUID) -> Dict:
        """Get comprehensive availability for a parking lot.
        
        Args:
            parking_lot_id: Parking lot ID
            
        Returns:
            Dictionary with availability details
        """
        lot = self.lot_repo.get_with_floors(parking_lot_id)
        if not lot:
            raise ValueError(f"Parking lot {parking_lot_id} not found")
        
        # Get availability stats
        stats_by_type = self.spot_repo.get_availability_stats(parking_lot_id)
        
        # Calculate totals
        total_spots = sum(s['total'] for s in stats_by_type.values())
        available_spots = sum(s['available'] for s in stats_by_type.values())
        
        # Get floor-wise availability
        availability_by_floor = []
        for floor in lot.floors:
            floor_stats = {
                'floor_number': floor.floor_number,
                'total_spots': floor.total_spots,
                'available_spots': len([s for s in floor.spots if s.status.value == 'AVAILABLE'])
            }
            availability_by_floor.append(floor_stats)
        
        return {
            'lot_id': str(parking_lot_id),
            'lot_name': lot.name,
            'total_spots': total_spots,
            'available_spots': available_spots,
            'occupancy_rate': round((total_spots - available_spots) / total_spots if total_spots > 0 else 0, 2),
            'availability_by_type': stats_by_type,
            'availability_by_floor': availability_by_floor
        }
