from typing import List, Dict, Set
from src.model.location import Location

class SpatialIndex:
    """
    A simple Grid-based Spatial Index.
    Divides the world into cells of fixed size (LAT/LON DEGREES).
    """
    def __init__(self, cell_size_degrees: float = 0.01):
        # 0.01 degrees is approx 1.11 km
        self._cell_size = cell_size_degrees
        self._grid: Dict[str, Set['Driver']] = {} # CellID -> Set of Drivers

    def _get_cell_id(self, location: Location) -> str:
        x = int(location.latitude / self._cell_size)
        y = int(location.longitude / self._cell_size)
        return f"{x},{y}"

    def update(self, driver: 'Driver'):
        """Adds or updates a driver in the grid."""
        cell_id = self._get_cell_id(driver.location)
        if cell_id not in self._grid:
             self._grid[cell_id] = set()
        self._grid[cell_id].add(driver)

    def search(self, center: Location, radius_km: float = 2.0) -> List['Driver']:
        """
        Returns drivers in the cell containing 'center' and its neighbors.
        For simplicity, we just check the 9-cell neighborhood (Moore neighborhood).
        radius_km is essentially ignored in this simplified grid lookup, 
        we rely on the grid cell size approx.
        """
        center_x = int(center.latitude / self._cell_size)
        center_y = int(center.longitude / self._cell_size)
        
        nearby_drivers = []
        
        # Check current cell and 8 neighbors
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell_key = f"{center_x + dx},{center_y + dy}"
                if cell_key in self._grid:
                    nearby_drivers.extend(list(self._grid[cell_key]))
                    
        return nearby_drivers
