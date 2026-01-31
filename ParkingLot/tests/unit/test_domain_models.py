"""Unit tests for domain models."""
import pytest
from datetime import datetime

from src.domain.enums import VehicleType, SpotType, SpotStatus, TicketStatus
from src.domain.models.vehicle import Vehicle
from src.domain.models.parking_lot import ParkingSpot, Floor, ParkingLot
from src.domain.models.ticket import Ticket


class TestVehicle:
    """Tests for Vehicle entity."""
    
    def test_create_vehicle(self):
        """Test vehicle creation."""
        vehicle = Vehicle(
            license_plate="ABC123",
            vehicle_type=VehicleType.CAR,
            owner_name="John Doe"
        )
        assert vehicle.license_plate == "ABC123"
        assert vehicle.vehicle_type == VehicleType.CAR
        assert not vehicle.is_electric()
    
    def test_electric_vehicle(self):
        """Test electric vehicle detection."""
        ev = Vehicle(
            license_plate="EV001",
            vehicle_type=VehicleType.ELECTRIC_CAR
        )
        assert ev.is_electric()
    
    def test_license_plate_normalization(self):
        """Test license plate normalization."""
        vehicle = Vehicle(
            license_plate="abc 123",
            vehicle_type=VehicleType.CAR
        )
        assert vehicle.license_plate == "ABC123"
    
    def test_invalid_license_plate(self):
        """Test invalid license plate."""
        with pytest.raises(ValueError):
            Vehicle(license_plate="12", vehicle_type=VehicleType.CAR)
    
    def test_compatible_spot_types(self):
        """Test compatible spot types for vehicles."""
        car = Vehicle(license_plate="CAR001", vehicle_type=VehicleType.CAR)
        compatible = car.get_compatible_spot_types()
        assert SpotType.COMPACT in compatible
        assert SpotType.LARGE in compatible
        
        motorcycle = Vehicle(license_plate="MOTO01", vehicle_type=VehicleType.MOTORCYCLE)
        compatible = motorcycle.get_compatible_spot_types()
        assert SpotType.MOTORCYCLE in compatible
        assert SpotType.COMPACT in compatible


class TestParkingSpot:
    """Tests for ParkingSpot entity."""
    
    def test_create_spot(self):
        """Test spot creation."""
        from uuid import uuid4
        floor_id = uuid4()
        
        spot = ParkingSpot(
            spot_number="A1",
            spot_type=SpotType.COMPACT,
            floor_id=floor_id
        )
        assert spot.spot_number == "A1"
        assert spot.is_available()
    
    def test_occupy_spot(self):
        """Test spot occupation."""
        from uuid import uuid4
        spot = ParkingSpot(
            spot_number="A1",
            spot_type=SpotType.COMPACT,
            floor_id=uuid4()
        )
        spot.occupy()
        assert not spot.is_available()
        assert spot.status == SpotStatus.OCCUPIED
    
    def test_vacate_spot(self):
        """Test spot vacation."""
        from uuid import uuid4
        spot = ParkingSpot(
            spot_number="A1",
            spot_type=SpotType.COMPACT,
            floor_id=uuid4()
        )
        spot.occupy()
        spot.vacate()
        assert spot.is_available()
    
    def test_cannot_occupy_occupied_spot(self):
        """Test cannot occupy already occupied spot."""
        from uuid import uuid4
        spot = ParkingSpot(
            spot_number="A1",
            spot_type=SpotType.COMPACT,
            floor_id=uuid4()
        )
        spot.occupy()
        with pytest.raises(ValueError):
            spot.occupy()


class TestTicket:
    """Tests for Ticket entity."""
    
    def test_create_ticket(self):
        """Test ticket creation."""
        from uuid import uuid4
        ticket = Ticket(
            ticket_number="TKT-001",
            parking_lot_id=uuid4(),
            spot_id=uuid4(),
            vehicle_id=uuid4(),
            entry_time=datetime.utcnow()
        )
        assert ticket.is_active()
    
    def test_duration_calculation(self):
        """Test duration calculation."""
        from uuid import uuid4
        entry = datetime(2024, 1, 1, 10, 0, 0)
        exit = datetime(2024, 1, 1, 13, 30, 0)
        
        ticket = Ticket(
            ticket_number="TKT-001",
            parking_lot_id=uuid4(),
            spot_id=uuid4(),
            vehicle_id=uuid4(),
            entry_time=entry
        )
        ticket.set_exit_time(exit)
        
        duration = ticket.get_duration_hours()
        assert duration == 3.5
    
    def test_mark_as_paid(self):
        """Test marking ticket as paid."""
        from uuid import uuid4
        ticket = Ticket(
            ticket_number="TKT-001",
            parking_lot_id=uuid4(),
            spot_id=uuid4(),
            vehicle_id=uuid4(),
            entry_time=datetime.utcnow()
        )
        ticket.mark_as_paid()
        assert ticket.status == TicketStatus.PAID


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
