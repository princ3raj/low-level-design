"""Base domain entity class."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class BaseEntity:
    """Base class for all domain entities."""
    
    def __init__(self, id: Optional[UUID] = None):
        """Initialize base entity with optional ID."""
        self.id: UUID = id or uuid4()
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Compare entities by ID."""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(id={self.id})"
