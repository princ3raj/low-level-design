"""Singleton pattern for ParkingLotManager."""
from threading import Lock
from typing import Dict, Optional
from uuid import UUID

from src.domain.models.parking_lot import ParkingLot


class ParkingLotManager:
    """Singleton manager for all parking lots in the system.
    
    This ensures a single point of control for managing parking lots.
    Thread-safe implementation using double-checked locking.
    """
    
    _instance: Optional['ParkingLotManager'] = None
    _lock: Lock = Lock()
    
    def __new__(cls):
        """Create or return existing singleton instance."""
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize manager (only once)."""
        if self._initialized:
            return
        
        self._lots: Dict[UUID, ParkingLot] = {}
        self._lock = Lock()
        self._initialized = True
    
    def add_parking_lot(self, lot: ParkingLot) -> None:
        """Add a parking lot to the manager.
        
        Args:
            lot: ParkingLot instance to add
        """
        with self._lock:
            self._lots[lot.id] = lot
    
    def get_parking_lot(self, lot_id: UUID) -> Optional[ParkingLot]:
        """Get a parking lot by ID.
        
        Args:
            lot_id: UUID of the parking lot
            
        Returns:
            ParkingLot instance or None if not found
        """
        return self._lots.get(lot_id)
    
    def remove_parking_lot(self, lot_id: UUID) -> bool:
        """Remove a parking lot from the manager.
        
        Args:
            lot_id: UUID of the parking lot to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if lot_id in self._lots:
                del self._lots[lot_id]
                return True
            return False
    
    def get_all_lots(self) -> Dict[UUID, ParkingLot]:
        """Get all parking lots.
        
        Returns:
            Dictionary of lot_id to ParkingLot
        """
        return self._lots.copy()
    
    def get_total_lots(self) -> int:
        """Get total number of parking lots.
        
        Returns:
            Number of parking lots
        """
        return len(self._lots)
    
    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (mainly for testing)."""
        with cls._lock:
            cls._instance = None
