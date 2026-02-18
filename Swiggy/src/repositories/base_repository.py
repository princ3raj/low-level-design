"""Base repository with CRUD operations using Repository pattern"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for all entities"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would use a real database
        self._storage: Dict[str, T] = {}
    
    def save(self, entity: T) -> T:
        """Save or update an entity"""
        entity_id = self._get_entity_id(entity)
        self._storage[entity_id] = entity
        return entity
    
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID"""
        return self._storage.get(entity_id)
    
    def find_all(self) -> List[T]:
        """Get all entities"""
        return list(self._storage.values())
    
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        return entity_id in self._storage
    
    def count(self) -> int:
        """Count total entities"""
        return len(self._storage)
    
    @abstractmethod
    def _get_entity_id(self, entity: T) -> str:
        """Get the ID field from entity (must be implemented by subclasses)"""
        pass
    
    def clear_all(self):
        """Clear all data (useful for testing)"""
        self._storage.clear()
