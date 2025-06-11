import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domain.entities.session import Session, SessionStatus
from domain.exceptions.custom_exceptions import ValidationError

def test_create_session():
    """Testa a criação de uma sessão com dados válidos."""
    session = Session(
        id=1,
        user_address="0x1234567890123456789012345678901234567890",
        station_id=1,
        start_time=datetime.utcnow(),
        end_time=None,
        status=SessionStatus.ACTIVE,
        payment_amount=None,
        payment_time=None
    )
    
    assert session.id == 1
    assert session.user_address == "0x1234567890123456789012345678901234567890"
    assert session.station_id == 1
    assert isinstance(session.start_time, datetime)
    assert session.end_time is None
    assert session.status == SessionStatus.ACTIVE
    assert session.payment_amount is None
    assert session.payment_time is None

def test_start_session(mock_session):
    """Testa o início de uma sessão."""
    start_time = datetime.utcnow()
    mock_session.start(start_time)
    
    assert mock_session.start_time == start_time
    assert mock_session.status == SessionStatus.ACTIVE
    assert mock_session.end_time is None
    assert mock_session.payment_amount is None
    assert mock_session.payment_time is None

def test_end_session(mock_session):
    """Testa o fim de uma sessão."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    
    assert mock_session.end_time == end_time
    assert mock_session.status == SessionStatus.COMPLETED
    assert mock_session.duration == timedelta(hours=2)

def test_pay_session(mock_session):
    """Testa o pagamento de uma sessão."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    payment_time = end_time + timedelta(minutes=5)
    amount = Decimal('0.002')
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    mock_session.pay(amount, payment_time)
    
    assert mock_session.payment_amount == amount
    assert mock_session.payment_time == payment_time
    assert mock_session.status == SessionStatus.PAID

def test_cancel_session(mock_session):
    """Testa o cancelamento de uma sessão."""
    start_time = datetime.utcnow()
    mock_session.start(start_time)
    mock_session.cancel()
    
    assert mock_session.status == SessionStatus.CANCELLED
    assert mock_session.end_time is None
    assert mock_session.payment_amount is None
    assert mock_session.payment_time is None

def test_get_duration(mock_session):
    """Testa o cálculo da duração de uma sessão."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2, minutes=30)
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    
    assert mock_session.duration == timedelta(hours=2, minutes=30)
    assert mock_session.duration_hours == Decimal('2.5')

def test_to_dict(mock_session):
    """Testa a conversão da sessão para dicionário."""
    session_dict = mock_session.to_dict()
    
    assert isinstance(session_dict, dict)
    assert session_dict["id"] == mock_session.id
    assert session_dict["user_address"] == mock_session.user_address
    assert session_dict["station_id"] == mock_session.station_id
    assert isinstance(session_dict["start_time"], str)
    assert session_dict["end_time"] is None
    assert session_dict["status"] == mock_session.status.value
    assert session_dict["payment_amount"] is None
    assert session_dict["payment_time"] is None

def test_from_dict():
    """Testa a criação de uma sessão a partir de um dicionário."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    payment_time = end_time + timedelta(minutes=5)
    
    data = {
        "id": 1,
        "user_address": "0x1234567890123456789012345678901234567890",
        "station_id": 1,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": SessionStatus.PAID.value,
        "payment_amount": "0.002",
        "payment_time": payment_time.isoformat()
    }
    
    session = Session.from_dict(data)
    
    assert session.id == data["id"]
    assert session.user_address == data["user_address"]
    assert session.station_id == data["station_id"]
    assert session.start_time == start_time
    assert session.end_time == end_time
    assert session.status == SessionStatus.PAID
    assert session.payment_amount == Decimal(data["payment_amount"])
    assert session.payment_time == payment_time

def test_start_already_started_session(mock_session):
    """Testa o início de uma sessão já iniciada."""
    mock_session.start(datetime.utcnow())
    
    with pytest.raises(ValidationError):
        mock_session.start(datetime.utcnow())

def test_end_not_started_session():
    """Testa o fim de uma sessão não iniciada."""
    session = Session(
        id=1,
        user_address="0x1234567890123456789012345678901234567890",
        station_id=1
    )
    
    with pytest.raises(ValidationError):
        session.end(datetime.utcnow())

def test_end_already_ended_session(mock_session):
    """Testa o fim de uma sessão já finalizada."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    
    with pytest.raises(ValidationError):
        mock_session.end(end_time + timedelta(hours=1))

def test_pay_not_ended_session(mock_session):
    """Testa o pagamento de uma sessão não finalizada."""
    mock_session.start(datetime.utcnow())
    
    with pytest.raises(ValidationError):
        mock_session.pay(Decimal('0.001'), datetime.utcnow())

def test_pay_already_paid_session(mock_session):
    """Testa o pagamento de uma sessão já paga."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    payment_time = end_time + timedelta(minutes=5)
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    mock_session.pay(Decimal('0.001'), payment_time)
    
    with pytest.raises(ValidationError):
        mock_session.pay(Decimal('0.001'), payment_time + timedelta(minutes=5))

def test_cancel_not_started_session():
    """Testa o cancelamento de uma sessão não iniciada."""
    session = Session(
        id=1,
        user_address="0x1234567890123456789012345678901234567890",
        station_id=1
    )
    
    with pytest.raises(ValidationError):
        session.cancel()

def test_cancel_already_ended_session(mock_session):
    """Testa o cancelamento de uma sessão já finalizada."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    
    with pytest.raises(ValidationError):
        mock_session.cancel()

def test_negative_payment_amount(mock_session):
    """Testa o pagamento com valor negativo."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=2)
    
    mock_session.start(start_time)
    mock_session.end(end_time)
    
    with pytest.raises(ValidationError):
        mock_session.pay(Decimal('-0.001'), datetime.utcnow())

def test_get_duration_not_ended_session(mock_session):
    """Testa o cálculo da duração de uma sessão não finalizada."""
    mock_session.start(datetime.utcnow())
    
    with pytest.raises(ValidationError):
        _ = mock_session.duration 