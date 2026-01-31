"""Observer pattern for availability updates."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from uuid import UUID


class Observer(ABC):
    """Abstract observer interface."""
    
    @abstractmethod
    def update(self, subject: 'Subject', event_data: Dict[str, Any]) -> None:
        """Receive update from subject.
        
        Args:
            subject: The subject that triggered the update
            event_data: Data associated with the event
        """
        pass


class Subject(ABC):
    """Abstract subject interface."""
    
    def __init__(self):
        """Initialize subject with empty observer list."""
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer.
        
        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer.
        
        Args:
            observer: Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_data: Dict[str, Any]) -> None:
        """Notify all observers of an event.
        
        Args:
            event_data: Data associated with the event
        """
        for observer in self._observers:
            observer.update(self, event_data)


class AvailabilityObserver(Observer):
    """Observer for parking availability changes."""
    
    def __init__(self, name: str):
        """Initialize availability observer.
        
        Args:
            name: Name/identifier for this observer
        """
        self.name = name
        self.last_event: Dict[str, Any] = {}
    
    def update(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """Handle availability update.
        
        Args:
            subject: The parking lot or spot that changed
            event_data: Event data including:
                - event_type: 'spot_occupied' or 'spot_available'
                - parking_lot_id: UUID of parking lot
                - spot_id: UUID of spot
                - spot_number: Spot identifier
                - spot_type: Type of spot
        """
        self.last_event = event_data
        event_type = event_data.get('event_type')
        
        if event_type == 'spot_occupied':
            self._handle_spot_occupied(event_data)
        elif event_type == 'spot_available':
            self._handle_spot_available(event_data)
    
    def _handle_spot_occupied(self, event_data: Dict[str, Any]) -> None:
        """Handle spot occupied event.
        
        Args:
            event_data: Event data
        """
        spot_number = event_data.get('spot_number')
        print(f"[{self.name}] Spot {spot_number} is now OCCUPIED")
    
    def _handle_spot_available(self, event_data: Dict[str, Any]) -> None:
        """Handle spot available event.
        
        Args:
            event_data: Event data
        """
        spot_number = event_data.get('spot_number')
        print(f"[{self.name}] Spot {spot_number} is now AVAILABLE")


class CacheInvalidationObserver(Observer):
    """Observer for invalidating availability cache."""
    
    def __init__(self):
        """Initialize cache invalidation observer."""
        self.invalidated_lots: set = set()
    
    def update(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """Invalidate cache for parking lot.
        
        Args:
            subject: The parking lot that changed
            event_data: Event data with parking_lot_id
        """
        lot_id = event_data.get('parking_lot_id')
        if lot_id:
            self.invalidated_lots.add(lot_id)
            # In real implementation, this would call cache.delete(f"availability:{lot_id}")
            print(f"[Cache] Invalidated availability cache for lot {lot_id}")
    
    def clear_invalidated(self) -> None:
        """Clear the set of invalidated lots."""
        self.invalidated_lots.clear()


class NotificationObserver(Observer):
    """Observer for sending notifications to users."""
    
    def __init__(self):
        """Initialize notification observer."""
        self.notifications: List[Dict[str, Any]] = []
    
    def update(self, subject: Subject, event_data: Dict[str, Any]) -> None:
        """Send notification based on event.
        
        Args:
            subject: The subject that triggered the event
            event_data: Event data
        """
        event_type = event_data.get('event_type')
        
        # Only notify on spots becoming available in high-demand scenarios
        if event_type == 'spot_available':
            notification = {
                'type': 'spot_available',
                'message': f"Spot {event_data.get('spot_number')} is now available",
                'lot_id': event_data.get('parking_lot_id'),
                'spot_type': event_data.get('spot_type')
            }
            self.notifications.append(notification)
            # In real implementation, this would send push notification/SMS
            print(f"[Notification] {notification['message']}")
