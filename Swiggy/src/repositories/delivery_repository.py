"""Delivery repository"""
from typing import List, Optional
from .base_repository import BaseRepository
from ..domain.models.delivery import Delivery
from ..domain.enums import DeliveryStatus


class DeliveryRepository(BaseRepository[Delivery]):
    """Repository for delivery entities"""
    
    def _get_entity_id(self, entity: Delivery) -> str:
        return entity.id
    
    def find_by_order(self, order_id: str) -> Optional[Delivery]:
        """Find delivery by order ID"""
        for delivery in self._storage.values():
            if delivery.order_id == order_id:
                return delivery
        return None
    
    def find_by_partner(self, partner_id: str) -> List[Delivery]:
        """Find all deliveries for a partner"""
        deliveries = [
            d for d in self._storage.values()
            if d.delivery_partner_id == partner_id
        ]
        deliveries.sort(key=lambda d: d.assigned_at, reverse=True)
        return deliveries
    
    def find_active_deliveries(self, partner_id: str) -> List[Delivery]:
        """Find active (non-delivered) deliveries for a partner"""
        return [
            d for d in self._storage.values()
            if (d.delivery_partner_id == partner_id and 
                d.status != DeliveryStatus.DELIVERED)
        ]
    
    def find_by_status(self, status: DeliveryStatus) -> List[Delivery]:
        """Find deliveries by status"""
        return [
            d for d in self._storage.values()
            if d.status == status
        ]
