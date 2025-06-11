import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domain.entities.station import Station
from domain.exceptions.custom_exceptions import (
    ValidationError,
    ResourceConflictError
)

def test_create_station():
    """Testa a criação de uma estação com dados válidos."""
    station = Station(
        id=1,
        location="Test Location",
        power_output=Decimal('7.4'),
        price_per_hour=Decimal('0.001'),
        is_available=True,
        current_session_id=None,
        reservations={},
        total_sessions=0,
        total_revenue=Decimal('0.0')
    )
    
    assert station.id == 1
    assert station.location == "Test Location"
    assert station.power_output == Decimal('7.4')
    assert station.price_per_hour == Decimal('0.001')
    assert station.is_available is True
    assert station.current_session_id is None
    assert station.reservations == {}
    assert station.total_sessions == 0
    assert station.total_revenue == Decimal('0.0')

def test_add_reservation(mock_station):
    """Testa a adição de uma reserva."""
    user_address = "0x1234567890123456789012345678901234567890"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    mock_station.add_reservation(user_address, start_time, end_time)
    
    date_key = start_time.date().isoformat()
    assert date_key in mock_station.reservations
    assert len(mock_station.reservations[date_key]) == 1
    assert mock_station.reservations[date_key][0]["user_address"] == user_address
    assert mock_station.reservations[date_key][0]["start_time"] == start_time
    assert mock_station.reservations[date_key][0]["end_time"] == end_time

def test_remove_reservation(mock_station):
    """Testa a remoção de uma reserva."""
    user_address = "0x1234567890123456789012345678901234567890"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    mock_station.add_reservation(user_address, start_time, end_time)
    mock_station.remove_reservation(user_address, start_time)
    
    date_key = start_time.date().isoformat()
    assert date_key not in mock_station.reservations or len(mock_station.reservations[date_key]) == 0

def test_is_reserved_at(mock_station):
    """Testa a verificação de reserva em um horário específico."""
    user_address = "0x1234567890123456789012345678901234567890"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    mock_station.add_reservation(user_address, start_time, end_time)
    
    # Testa horário dentro da reserva
    assert mock_station.is_reserved_at(start_time + timedelta(minutes=30))
    
    # Testa horário fora da reserva
    assert not mock_station.is_reserved_at(start_time + timedelta(hours=3))

def test_get_reservation_user(mock_station):
    """Testa a obtenção do usuário que fez uma reserva."""
    user_address = "0x1234567890123456789012345678901234567890"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    mock_station.add_reservation(user_address, start_time, end_time)
    
    assert mock_station.get_reservation_user(start_time + timedelta(minutes=30)) == user_address
    assert mock_station.get_reservation_user(start_time + timedelta(hours=3)) is None

def test_start_session(mock_station):
    """Testa o início de uma sessão."""
    session_id = 1
    mock_station.start_session(session_id)
    
    assert mock_station.current_session_id == session_id
    assert not mock_station.is_available
    assert mock_station.total_sessions == 1

def test_end_session(mock_station):
    """Testa o fim de uma sessão."""
    session_id = 1
    mock_station.start_session(session_id)
    mock_station.end_session()
    
    assert mock_station.current_session_id is None
    assert mock_station.is_available

def test_add_revenue(mock_station):
    """Testa a adição de receita."""
    amount = Decimal('0.001')
    mock_station.add_revenue(amount)
    
    assert mock_station.total_revenue == amount

def test_to_dict(mock_station):
    """Testa a conversão da estação para dicionário."""
    station_dict = mock_station.to_dict()
    
    assert isinstance(station_dict, dict)
    assert station_dict["id"] == mock_station.id
    assert station_dict["location"] == mock_station.location
    assert isinstance(station_dict["power_output"], str)
    assert isinstance(station_dict["price_per_hour"], str)
    assert station_dict["is_available"] == mock_station.is_available
    assert station_dict["current_session_id"] == mock_station.current_session_id
    assert isinstance(station_dict["reservations"], dict)
    assert station_dict["total_sessions"] == mock_station.total_sessions
    assert isinstance(station_dict["total_revenue"], str)

def test_from_dict():
    """Testa a criação de uma estação a partir de um dicionário."""
    data = {
        "id": 1,
        "location": "Test Location",
        "power_output": "7.4",
        "price_per_hour": "0.001",
        "is_available": True,
        "current_session_id": None,
        "reservations": {
            "2024-02-20": [{
                "user_address": "0x1234567890123456789012345678901234567890",
                "start_time": datetime.utcnow().isoformat(),
                "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat()
            }]
        },
        "total_sessions": 1,
        "total_revenue": "0.001"
    }
    
    station = Station.from_dict(data)
    
    assert station.id == data["id"]
    assert station.location == data["location"]
    assert station.power_output == Decimal(data["power_output"])
    assert station.price_per_hour == Decimal(data["price_per_hour"])
    assert station.is_available == data["is_available"]
    assert station.current_session_id == data["current_session_id"]
    assert isinstance(station.reservations, dict)
    assert station.total_sessions == data["total_sessions"]
    assert station.total_revenue == Decimal(data["total_revenue"])

def test_invalid_power_output():
    """Testa a criação de uma estação com potência inválida."""
    with pytest.raises(ValidationError):
        Station(
            id=1,
            location="Test Location",
            power_output=Decimal('-7.4'),
            price_per_hour=Decimal('0.001'),
            is_available=True
        )

def test_invalid_price():
    """Testa a criação de uma estação com preço inválido."""
    with pytest.raises(ValidationError):
        Station(
            id=1,
            location="Test Location",
            power_output=Decimal('7.4'),
            price_per_hour=Decimal('-0.001'),
            is_available=True
        )

def test_duplicate_reservation(mock_station):
    """Testa a adição de uma reserva duplicada."""
    user_address = "0x1234567890123456789012345678901234567890"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    mock_station.add_reservation(user_address, start_time, end_time)
    
    with pytest.raises(ResourceConflictError):
        mock_station.add_reservation(user_address, start_time, end_time)

def test_reservation_overlap(mock_station):
    """Testa a adição de uma reserva com sobreposição de horário."""
    user_address = "0x1234567890123456789012345678901234567890"
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    mock_station.add_reservation(user_address, start_time, end_time)
    
    with pytest.raises(ResourceConflictError):
        mock_station.add_reservation(
            "0x0987654321098765432109876543210987654321",
            start_time + timedelta(minutes=30),
            end_time + timedelta(minutes=30)
        )

def test_remove_nonexistent_reservation(mock_station):
    """Testa a remoção de uma reserva inexistente."""
    with pytest.raises(ValidationError):
        mock_station.remove_reservation(
            "0x1234567890123456789012345678901234567890",
            datetime.utcnow()
        )

def test_start_session_when_busy(mock_station):
    """Testa o início de uma sessão quando a estação está ocupada."""
    mock_station.start_session(1)
    
    with pytest.raises(ResourceConflictError):
        mock_station.start_session(2)

def test_end_session_when_free(mock_station):
    """Testa o fim de uma sessão quando a estação está livre."""
    with pytest.raises(ValidationError):
        mock_station.end_session()

def test_negative_revenue(mock_station):
    """Testa a adição de receita negativa."""
    with pytest.raises(ValidationError):
        mock_station.add_revenue(Decimal('-0.001')) 