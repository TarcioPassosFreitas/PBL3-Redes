import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock

from domain.entities.user import User
from domain.entities.station import Station
from domain.entities.session import Session, SessionStatus
from domain.ports.http_port import HTTPPort
from domain.ports.blockchain_port import BlockchainPort
from adapters.http.flask_adapter import FlaskAdapter
from adapters.blockchain.web3_adapter import Web3Adapter

# Fixtures para entidades
@pytest.fixture
def mock_user():
    """Fixture que retorna um usuário de teste."""
    return User(
        wallet_address="0x1234567890123456789012345678901234567890",
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
        active_sessions=[],
        total_charges=Decimal('0.0'),
        total_sessions=0,
        active_reservations=[]
    )

@pytest.fixture
def mock_station():
    """Fixture que retorna uma estação de teste."""
    return Station(
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

@pytest.fixture
def mock_session():
    """Fixture que retorna uma sessão de teste."""
    return Session(
        id=1,
        user_address="0x1234567890123456789012345678901234567890",
        station_id=1,
        start_time=datetime.utcnow(),
        end_time=None,
        status=SessionStatus.ACTIVE,
        payment_amount=None,
        payment_time=None
    )

# Fixtures para adaptadores
@pytest.fixture
def mock_http_port():
    """Fixture que retorna um mock do adaptador HTTP."""
    mock = AsyncMock(spec=HTTPPort)
    
    # Configurar comportamentos padrão
    mock.validate_wallet_address.return_value = True
    mock.validate_signature.return_value = True
    mock.parse_datetime.return_value = datetime.utcnow()
    mock.parse_decimal.return_value = Decimal('0.001')
    mock.create_response.return_value = {"success": True, "data": {}}
    mock.handle_error.return_value = {"success": False, "error": "Test error"}
    
    return mock

@pytest.fixture
def mock_blockchain_port():
    """Fixture que retorna um mock do adaptador Blockchain."""
    mock = AsyncMock(spec=BlockchainPort)
    
    # Configurar comportamentos padrão
    mock.get_user.return_value = mock_user()
    mock.get_station.return_value = mock_station()
    mock.get_session.return_value = mock_session()
    mock.verify_signature.return_value = True
    mock.get_eth_balance.return_value = Decimal('1.0')
    
    return mock

# Fixtures para casos de uso
@pytest.fixture
def mock_charge_use_case(mock_http_port, mock_blockchain_port):
    """Fixture que retorna um caso de uso de carregamento com mocks."""
    from domain.use_cases.charge import ChargeUseCase
    return ChargeUseCase(
        http_port=mock_http_port,
        blockchain_port=mock_blockchain_port
    )

@pytest.fixture
def mock_payment_use_case(mock_http_port, mock_blockchain_port):
    """Fixture que retorna um caso de uso de pagamento com mocks."""
    from domain.use_cases.pay import PaymentUseCase
    return PaymentUseCase(
        http_port=mock_http_port,
        blockchain_port=mock_blockchain_port
    )

# Fixtures para dados de teste
@pytest.fixture
def valid_wallet_address():
    """Fixture que retorna um endereço de carteira válido."""
    return "0x1234567890123456789012345678901234567890"

@pytest.fixture
def valid_signature():
    """Fixture que retorna uma assinatura válida."""
    return "0x1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"

@pytest.fixture
def valid_datetime_str():
    """Fixture que retorna uma string de data/hora válida."""
    return datetime.utcnow().isoformat()

@pytest.fixture
def valid_reservation_data():
    """Fixture que retorna dados válidos para uma reserva."""
    start_time = datetime.utcnow() + timedelta(hours=1)
    return {
        "station_id": 1,
        "start_time": start_time.isoformat(),
        "duration_hours": 2
    }

@pytest.fixture
def valid_session_data():
    """Fixture que retorna dados válidos para uma sessão."""
    return {
        "station_id": 1,
        "wallet_address": "0x1234567890123456789012345678901234567890",
        "signature": "0x1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    }

@pytest.fixture
def valid_payment_data():
    """Fixture que retorna dados válidos para um pagamento."""
    return {
        "session_id": 1,
        "amount": "0.001",
        "wallet_address": "0x1234567890123456789012345678901234567890",
        "signature": "0x1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    } 