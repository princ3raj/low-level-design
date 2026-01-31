"""Base repository pattern."""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from src.infrastructure.database.connection import Base

# Generic type for models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Base repository with CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        """Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def create(self, entity: ModelType) -> ModelType:
        """Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity
        """
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of entities
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, entity: ModelType) -> ModelType:
        """Update an entity.
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity
        """
        self.db.flush()
        self.db.refresh(entity)
        return entity
    
    def delete(self, id: UUID) -> bool:
        """Delete an entity.
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(id)
        if entity:
            self.db.delete(entity)
            self.db.flush()
            return True
        return False
    
    def count(self) -> int:
        """Get total count of entities.
        
        Returns:
            Total count
        """
        return self.db.query(self.model).count()
