import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domain.entities.user import User
from domain.exceptions.custom_exceptions import ValidationError

def test_create_user():
    """Testa a criação de um usuário com dados válidos."""
    user = User.create_new(
        wallet_address="0x1234567890123456789012345678901234567890",
        email="test@example.com",
        name="Test User"
    )
    
    assert user.wallet_address == "0x1234567890123456789012345678901234567890"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert isinstance(user.created_at, datetime)
    assert user.last_login is None
    assert user.active_sessions == []
    assert user.total_charges == Decimal('0.0')
    assert user.total_sessions == 0
    assert user.active_reservations == []

def test_create_user_minimal():
    """Testa a criação de um usuário apenas com endereço da carteira."""
    user = User.create_new(
        wallet_address="0x1234567890123456789012345678901234567890"
    )
    
    assert user.wallet_address == "0x1234567890123456789012345678901234567890"
    assert user.email is None
    assert user.name is None
    assert isinstance(user.created_at, datetime)
    assert user.last_login is None
    assert user.active_sessions == []
    assert user.total_charges == Decimal('0.0')
    assert user.total_sessions == 0
    assert user.active_reservations == []

def test_add_charge(mock_user):
    """Testa a adição de um valor de carregamento."""
    amount = Decimal('0.001')
    mock_user.add_charge(amount)
    
    assert mock_user.total_charges == amount

def test_add_session(mock_user):
    """Testa a adição de uma sessão ativa."""
    session_id = 1
    mock_user.add_session(session_id)
    
    assert session_id in mock_user.active_sessions
    assert mock_user.total_sessions == 1

def test_remove_session(mock_user):
    """Testa a remoção de uma sessão ativa."""
    session_id = 1
    mock_user.add_session(session_id)
    mock_user.remove_session(session_id)
    
    assert session_id not in mock_user.active_sessions

def test_add_reservation(mock_user):
    """Testa a adição de uma reserva."""
    reservation_id = 1
    mock_user.add_reservation(reservation_id)
    
    assert reservation_id in mock_user.active_reservations

def test_remove_reservation(mock_user):
    """Testa a remoção de uma reserva."""
    reservation_id = 1
    mock_user.add_reservation(reservation_id)
    mock_user.remove_reservation(reservation_id)
    
    assert reservation_id not in mock_user.active_reservations

def test_to_dict(mock_user):
    """Testa a conversão do usuário para dicionário."""
    user_dict = mock_user.to_dict()
    
    assert isinstance(user_dict, dict)
    assert user_dict["wallet_address"] == mock_user.wallet_address
    assert user_dict["email"] == mock_user.email
    assert user_dict["name"] == mock_user.name
    assert isinstance(user_dict["created_at"], str)
    assert isinstance(user_dict["last_login"], str) if mock_user.last_login else user_dict["last_login"] is None
    assert user_dict["active_sessions"] == mock_user.active_sessions
    assert isinstance(user_dict["total_charges"], str)
    assert user_dict["total_sessions"] == mock_user.total_sessions
    assert user_dict["active_reservations"] == mock_user.active_reservations

def test_from_dict():
    """Testa a criação de um usuário a partir de um dicionário."""
    data = {
        "wallet_address": "0x1234567890123456789012345678901234567890",
        "email": "test@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat(),
        "active_sessions": [1, 2],
        "total_charges": "0.001",
        "total_sessions": 2,
        "active_reservations": [1]
    }
    
    user = User.from_dict(data)
    
    assert user.wallet_address == data["wallet_address"]
    assert user.email == data["email"]
    assert user.name == data["name"]
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.last_login, datetime)
    assert user.active_sessions == data["active_sessions"]
    assert user.total_charges == Decimal(data["total_charges"])
    assert user.total_sessions == data["total_sessions"]
    assert user.active_reservations == data["active_reservations"]

def test_invalid_wallet_address():
    """Testa a criação de um usuário com endereço de carteira inválido."""
    with pytest.raises(ValidationError):
        User.create_new(wallet_address="invalid_address")

def test_negative_charge(mock_user):
    """Testa a adição de um valor de carregamento negativo."""
    with pytest.raises(ValidationError):
        mock_user.add_charge(Decimal('-0.001'))

def test_duplicate_session(mock_user):
    """Testa a adição de uma sessão duplicada."""
    session_id = 1
    mock_user.add_session(session_id)
    
    with pytest.raises(ValidationError):
        mock_user.add_session(session_id)

def test_remove_nonexistent_session(mock_user):
    """Testa a remoção de uma sessão inexistente."""
    with pytest.raises(ValidationError):
        mock_user.remove_session(1)

def test_duplicate_reservation(mock_user):
    """Testa a adição de uma reserva duplicada."""
    reservation_id = 1
    mock_user.add_reservation(reservation_id)
    
    with pytest.raises(ValidationError):
        mock_user.add_reservation(reservation_id)

def test_remove_nonexistent_reservation(mock_user):
    """Testa a remoção de uma reserva inexistente."""
    with pytest.raises(ValidationError):
        mock_user.remove_reservation(1) 