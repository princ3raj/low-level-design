"""Parking-related repositories."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from src.domain.enums import SpotStatus, SpotType
from src.infrastructure.database.models import (
    FloorModel,
    ParkingLotModel,
    ParkingSpotModel,
)
from src.infrastructure.repository.base_repository import BaseRepository


class ParkingLotRepository(BaseRepository[ParkingLotModel]):
    """Repository for parking lots."""
    
    def __init__(self, db: Session):
        """Initialize parking lot repository."""
        super().__init__(ParkingLotModel, db)
    
    def get_by_name(self, name: str) -> Optional[ParkingLotModel]:
        """Get parking lot by name.
        
        Args:
            name: Parking lot name
            
        Returns:
            ParkingLotModel or None
        """
        return self.db.query(self.model).filter(
            self.model.name == name
        ).first()
    
    def get_by_city(self, city: str, skip: int = 0, limit: int = 100) -> List[ParkingLotModel]:
        """Get parking lots by city.
        
        Args:
            city: City name
            skip: Records to skip
            limit: Max records
            
        Returns:
            List of parking lots
        """
        return self.db.query(self.model).filter(
            self.model.city == city
        ).offset(skip).limit(limit).all()
    
    def get_with_floors(self, lot_id: UUID) -> Optional[ParkingLotModel]:
        """Get parking lot with all floors eagerly loaded.
        
        Args:
            lot_id: Parking lot ID
            
        Returns:
            ParkingLotModel with floors or None
        """
        return self.db.query(self.model).options(
            joinedload(self.model.floors)
        ).filter(self.model.id == lot_id).first()


class FloorRepository(BaseRepository[FloorModel]):
    """Repository for floors."""
    
    def __init__(self, db: Session):
        """Initialize floor repository."""
        super().__init__(FloorModel, db)
    
    def get_by_parking_lot(self, parking_lot_id: UUID) -> List[FloorModel]:
        """Get all floors for a parking lot.
        
        Args:
            parking_lot_id: Parking lot ID
            
        Returns:
            List of floors
        """
        return self.db.query(self.model).filter(
            self.model.parking_lot_id == parking_lot_id
        ).order_by(self.model.floor_number).all()
    
    def get_by_floor_number(
        self,
        parking_lot_id: UUID,
        floor_number: int
    ) -> Optional[FloorModel]:
        """Get floor by number.
        
        Args:
            parking_lot_id: Parking lot ID
            floor_number: Floor number
            
        Returns:
            FloorModel or None
        """
        return self.db.query(self.model).filter(
            and_(
                self.model.parking_lot_id == parking_lot_id,
                self.model.floor_number == floor_number
            )
        ).first()


class ParkingSpotRepository(BaseRepository[ParkingSpotModel]):
    """Repository for parking spots."""
    
    def __init__(self, db: Session):
        """Initialize parking spot repository."""
        super().__init__(ParkingSpotModel, db)
    
    def get_available_spots(
        self,
        floor_id: UUID,
        spot_type: Optional[SpotType] = None
    ) -> List[ParkingSpotModel]:
        """Get available spots on a floor.
        
        Args:
            floor_id: Floor ID
            spot_type: Optional spot type filter
            
        Returns:
            List of available spots
        """
        query = self.db.query(self.model).filter(
            and_(
                self.model.floor_id == floor_id,
                self.model.status == SpotStatus.AVAILABLE
            )
        )
        
        if spot_type:
            query = query.filter(self.model.spot_type == spot_type)
        
        return query.all()
    
    def find_available_spot_for_vehicle(
        self,
        parking_lot_id: UUID,
        compatible_spot_types: List[SpotType],
        preferred_type: Optional[SpotType] = None
    ) -> Optional[ParkingSpotModel]:
        """Find an available spot for a vehicle.
        
        Uses optimistic locking to prevent race conditions.
        
        Args:
            parking_lot_id: Parking lot ID
            compatible_spot_types: List of compatible spot types
            preferred_type: Preferred spot type
            
        Returns:
            Available spot or None
        """
        # Build query for available spots
        from src.infrastructure.database.models import FloorModel
        
        query = self.db.query(self.model).join(
            FloorModel, self.model.floor_id == FloorModel.id
        ).filter(
            and_(
                FloorModel.parking_lot_id == parking_lot_id,
                self.model.status == SpotStatus.AVAILABLE,
                self.model.spot_type.in_(compatible_spot_types)
            )
        )
        
        # Try preferred type first
        if preferred_type and preferred_type in compatible_spot_types:
            spot = query.filter(self.model.spot_type == preferred_type).first()
            if spot:
                return spot
        
        # Find any compatible spot
        return query.first()
    
    def occupy_spot_with_lock(self, spot_id: UUID) -> bool:
        """Occupy a spot using optimistic locking.
        
        Args:
            spot_id: Spot ID
            
        Returns:
            True if successful, False if version conflict
        """
        spot = self.get_by_id(spot_id)
        if not spot or spot.status != SpotStatus.AVAILABLE:
            return False
        
        try:
            # Optimistic locking: update only if version matches
            result = self.db.query(self.model).filter(
                and_(
                    self.model.id == spot_id,
                    self.model.version == spot.version,
                    self.model.status == SpotStatus.AVAILABLE
                )
            ).update({
                "status": SpotStatus.OCCUPIED,
                "version": spot.version + 1,
                "updated_at": datetime.utcnow()
            }, synchronize_session=False)
            
            self.db.flush()
            return result > 0
            
        except IntegrityError:
            self.db.rollback()
            return False
    
    def vacate_spot(self, spot_id: UUID) -> bool:
        """Vacate a spot.
        
        Args:
            spot_id: Spot ID
            
        Returns:
            True if successful, False otherwise
        """
        spot = self.get_by_id(spot_id)
        if not spot or spot.status != SpotStatus.OCCUPIED:
            return False
        
        spot.status = SpotStatus.AVAILABLE
        spot.version += 1
        spot.updated_at = datetime.utcnow()
        self.db.flush()
        return True
    
    def get_availability_stats(self, parking_lot_id: UUID) -> dict:
        """Get availability statistics for a parking lot.
        
        Args:
            parking_lot_id: Parking lot ID
            
        Returns:
            Dictionary with availability stats by type
        """
        from sqlalchemy import func
        from src.infrastructure.database.models import FloorModel
        
        # Query for stats grouped by spot type
        stats = self.db.query(
            self.model.spot_type,
            func.count(self.model.id).label("total"),
            func.sum(
                func.cast(self.model.status == SpotStatus.AVAILABLE, Integer)
            ).label("available")
        ).join(
            FloorModel, self.model.floor_id == FloorModel.id
        ).filter(
            FloorModel.parking_lot_id == parking_lot_id
        ).group_by(self.model.spot_type).all()
        
        # Format results
        result = {}
        for spot_type, total, available in stats:
            result[spot_type.value] = {
                "total": total,
                "available": available or 0,
                "occupied": total - (available or 0)
            }
        
        return result
    
    def get_by_spot_number(
        self,
        floor_id: UUID,
        spot_number: str
    ) -> Optional[ParkingSpotModel]:
        """Get spot by number on a floor.
        
        Args:
            floor_id: Floor ID
            spot_number: Spot number
            
        Returns:
            ParkingSpotModel or None
        """
        return self.db.query(self.model).filter(
            and_(
                self.model.floor_id == floor_id,
                self.model.spot_number == spot_number
            )
        ).first()
