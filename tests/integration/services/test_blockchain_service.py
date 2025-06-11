import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address

from adapters.blockchain.blockchain_adapter import BlockchainAdapter
from repositories.blockchain_repository import BlockchainRepository
from services.blockchain_service import BlockchainService
from domain.entities.session import SessionStatus
from domain.entities.station import Station
from domain.entities.user import User
from domain.entities.reservation import Reservation
from domain.exceptions.custom_exceptions import (
    ValidationError,
    ResourceNotFoundError,
    ResourceConflictError,
    BlockchainError
)

@pytest.fixture
def web3():
    """Fixture que cria uma instância do Web3 para testes."""
    return Web3(Web3.HTTPProvider("http://localhost:8545"))

@pytest.fixture
def account():
    """Fixture que cria uma conta Ethereum para testes."""
    return Account.create()

@pytest.fixture
def contract_address(web3, account):
    """Fixture que implanta o contrato e retorna seu endereço."""
    # Compilar o contrato
    with open("contracts/EVCharging.sol", "r") as f:
        contract_source = f.read()
    
    # Deploy do contrato
    contract = web3.eth.contract(
        abi=contract_abi,  # ABI do contrato
        bytecode=contract_bytecode  # Bytecode do contrato
    )
    
    # Construir transação
    transaction = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": 2000000,
        "gasPrice": web3.eth.gas_price
    })
    
    # Assinar e enviar transação
    signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_receipt.contractAddress

@pytest.fixture
def blockchain_adapter(web3, contract_address):
    """Fixture que cria uma instância do adaptador blockchain para testes."""
    return BlockchainAdapter(web3, contract_address)

@pytest.fixture
def blockchain_repository(blockchain_adapter):
    """Fixture que cria uma instância do repositório blockchain para testes."""
    return BlockchainRepository(blockchain_adapter)

@pytest.fixture
def blockchain_service(blockchain_repository):
    """Fixture que cria uma instância do serviço blockchain para testes."""
    return BlockchainService(blockchain_repository)

@pytest.fixture
def valid_wallet_address(account):
    """Fixture que retorna um endereço de carteira válido para testes."""
    return to_checksum_address(account.address)

@pytest.fixture
def valid_signature(web3, account):
    """Fixture que retorna uma assinatura válida para testes."""
    message = "Test message"
    message_hash = web3.keccak(text=message)
    signed_message = web3.eth.account.sign_message(message_hash, account.key)
    return signed_message.signature.hex()

def test_register_user(blockchain_service, valid_wallet_address):
    """Testa o registro de um usuário."""
    user = blockchain_service.register_user(valid_wallet_address)
    
    assert isinstance(user, User)
    assert user.wallet_address == valid_wallet_address
    assert user.total_charges == 0
    assert len(user.active_sessions) == 0
    assert len(user.active_reservations) == 0

def test_get_user_profile(blockchain_service, valid_wallet_address):
    """Testa a obtenção do perfil de um usuário."""
    # Registrar usuário
    blockchain_service.register_user(valid_wallet_address)
    
    # Obter perfil
    profile = blockchain_service.get_user_profile(valid_wallet_address)
    
    assert isinstance(profile, dict)
    assert profile["wallet_address"] == valid_wallet_address
    assert profile["total_charges"] == 0
    assert len(profile["active_sessions"]) == 0
    assert len(profile["active_reservations"]) == 0
    assert "total_spent" in profile
    assert "average_session_duration" in profile
    assert "favorite_stations" in profile

def test_register_station(blockchain_service, valid_wallet_address):
    """Testa o registro de uma estação."""
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    
    station = blockchain_service.register_station(station_data)
    
    assert isinstance(station, Station)
    assert station.location == station_data["location"]
    assert station.power_output == station_data["power_output"]
    assert station.price_per_kwh == station_data["price_per_kwh"]
    assert station.owner_address == station_data["owner_address"]
    assert station.is_available is True
    assert station.total_revenue == 0

def test_get_station_details(blockchain_service, valid_wallet_address):
    """Testa a obtenção dos detalhes de uma estação."""
    # Registrar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    registered_station = blockchain_service.register_station(station_data)
    
    # Obter detalhes
    details = blockchain_service.get_station_details(registered_station.id)
    
    assert isinstance(details, dict)
    assert details["id"] == registered_station.id
    assert details["location"] == station_data["location"]
    assert details["power_output"] == station_data["power_output"]
    assert details["price_per_kwh"] == station_data["price_per_kwh"]
    assert details["owner_address"] == station_data["owner_address"]
    assert details["is_available"] is True
    assert details["total_revenue"] == 0
    assert "current_session" in details
    assert "upcoming_reservations" in details
    assert "rating" in details
    assert "total_sessions" in details

def test_start_charging_session(blockchain_service, valid_wallet_address, valid_signature):
    """Testa o início de uma sessão de carregamento."""
    # Registrar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    # Iniciar sessão
    session = blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    assert session.station_id == station.id
    assert session.wallet_address == valid_wallet_address
    assert session.status == SessionStatus.ACTIVE
    assert session.start_time is not None
    assert session.end_time is None
    assert session.payment_amount is None
    assert session.payment_time is None

def test_end_charging_session(blockchain_service, valid_wallet_address, valid_signature):
    """Testa o fim de uma sessão de carregamento."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    session = blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Finalizar sessão
    ended_session = blockchain_service.end_charging_session(session.id)
    
    assert ended_session.id == session.id
    assert ended_session.status == SessionStatus.COMPLETED
    assert ended_session.end_time is not None
    assert ended_session.payment_amount is None
    assert ended_session.payment_time is None
    assert "duration" in ended_session.__dict__
    assert "energy_consumed" in ended_session.__dict__
    assert "estimated_cost" in ended_session.__dict__

def test_process_session_payment(blockchain_service, valid_wallet_address, valid_signature):
    """Testa o processamento do pagamento de uma sessão."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    session = blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Finalizar sessão
    blockchain_service.end_charging_session(session.id)
    
    # Processar pagamento
    payment = blockchain_service.process_session_payment(
        session.id,
        valid_wallet_address,
        valid_signature
    )
    
    assert isinstance(payment, dict)
    assert payment["session_id"] == session.id
    assert payment["status"] == "paid"
    assert payment["amount"] is not None
    assert payment["timestamp"] is not None
    assert "transaction_hash" in payment
    assert "block_number" in payment

def test_create_charging_reservation(blockchain_service, valid_wallet_address, valid_signature):
    """Testa a criação de uma reserva de carregamento."""
    # Registrar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    # Criar reserva
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    reservation = blockchain_service.create_charging_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    assert isinstance(reservation, Reservation)
    assert reservation.station_id == station.id
    assert reservation.wallet_address == valid_wallet_address
    assert reservation.start_time == start_time
    assert reservation.end_time == end_time
    assert reservation.status == "active"

def test_cancel_charging_reservation(blockchain_service, valid_wallet_address, valid_signature):
    """Testa o cancelamento de uma reserva de carregamento."""
    # Registrar estação e criar reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    reservation = blockchain_service.create_charging_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    # Cancelar reserva
    cancelled_reservation = blockchain_service.cancel_charging_reservation(
        reservation.id,
        valid_wallet_address,
        valid_signature
    )
    
    assert cancelled_reservation.id == reservation.id
    assert cancelled_reservation.status == "cancelled"

def test_get_user_charging_history(blockchain_service, valid_wallet_address, valid_signature):
    """Testa a obtenção do histórico de carregamento de um usuário."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    session = blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    blockchain_service.end_charging_session(session.id)
    
    # Obter histórico
    history = blockchain_service.get_user_charging_history(valid_wallet_address)
    
    assert isinstance(history, dict)
    assert "sessions" in history
    assert "reservations" in history
    assert "statistics" in history
    assert len(history["sessions"]) > 0
    assert all(isinstance(session, dict) for session in history["sessions"])
    assert all("session_id" in session for session in history["sessions"])
    assert all("station_id" in session for session in history["sessions"])
    assert all("status" in session for session in history["sessions"])
    assert all("start_time" in session for session in history["sessions"])
    assert all("end_time" in session for session in history["sessions"])
    assert all("energy_consumed" in session for session in history["sessions"])
    assert all("cost" in session for session in history["sessions"])

def test_get_station_charging_history(blockchain_service, valid_wallet_address, valid_signature):
    """Testa a obtenção do histórico de carregamento de uma estação."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter histórico
    history = blockchain_service.get_station_charging_history(station.id)
    
    assert isinstance(history, dict)
    assert "sessions" in history
    assert "reservations" in history
    assert "statistics" in history
    assert len(history["sessions"]) > 0
    assert all(isinstance(session, dict) for session in history["sessions"])
    assert all("session_id" in session for session in history["sessions"])
    assert all("wallet_address" in session for session in history["sessions"])
    assert all("status" in session for session in history["sessions"])
    assert all("start_time" in session for session in history["sessions"])
    assert all("end_time" in session for session in history["sessions"])
    assert all("energy_consumed" in session for session in history["sessions"])
    assert all("revenue" in session for session in history["sessions"])

def test_get_user_payment_history(blockchain_service, valid_wallet_address, valid_signature):
    """Testa a obtenção do histórico de pagamentos de um usuário."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    session = blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    blockchain_service.end_charging_session(session.id)
    
    blockchain_service.process_session_payment(
        session.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter histórico
    history = blockchain_service.get_user_payment_history(valid_wallet_address)
    
    assert isinstance(history, list)
    assert len(history) > 0
    assert all(isinstance(payment, dict) for payment in history)
    assert all("session_id" in payment for payment in history)
    assert all("amount" in payment for payment in history)
    assert all("timestamp" in payment for payment in history)
    assert all("transaction_hash" in payment for payment in history)
    assert all("status" in payment for payment in history)

def test_get_station_revenue_history(blockchain_service, valid_wallet_address, valid_signature):
    """Testa a obtenção do histórico de receita de uma estação."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    session = blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    blockchain_service.end_charging_session(session.id)
    
    blockchain_service.process_session_payment(
        session.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter histórico
    history = blockchain_service.get_station_revenue_history(station.id)
    
    assert isinstance(history, dict)
    assert "payments" in history
    assert "statistics" in history
    assert len(history["payments"]) > 0
    assert all(isinstance(payment, dict) for payment in history["payments"])
    assert all("session_id" in payment for payment in history["payments"])
    assert all("amount" in payment for payment in history["payments"])
    assert all("timestamp" in payment for payment in history["payments"])
    assert all("transaction_hash" in payment for payment in history["payments"])
    assert all("wallet_address" in payment for payment in history["payments"])

def test_invalid_wallet_address(blockchain_service):
    """Testa operações com endereço de carteira inválido."""
    invalid_wallet = "0x0000000000000000000000000000000000000000"
    
    with pytest.raises(ValidationError):
        blockchain_service.register_user(invalid_wallet)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.get_user_profile(invalid_wallet)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.get_user_charging_history(invalid_wallet)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.get_user_payment_history(invalid_wallet)

def test_invalid_station_id(blockchain_service):
    """Testa operações com ID de estação inválido."""
    invalid_station_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.get_station_details(invalid_station_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.get_station_charging_history(invalid_station_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.get_station_revenue_history(invalid_station_id)

def test_invalid_session_id(blockchain_service):
    """Testa operações com ID de sessão inválido."""
    invalid_session_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.end_charging_session(invalid_session_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.process_session_payment(
            invalid_session_id,
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"
        )

def test_invalid_reservation_id(blockchain_service):
    """Testa operações com ID de reserva inválido."""
    invalid_reservation_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_service.cancel_charging_reservation(
            invalid_reservation_id,
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"
        )

def test_station_busy(blockchain_service, valid_wallet_address, valid_signature):
    """Testa operações em estação ocupada."""
    # Registrar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    blockchain_service.start_charging_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Tentar iniciar outra sessão
    with pytest.raises(ResourceConflictError):
        blockchain_service.start_charging_session(
            station.id,
            valid_wallet_address,
            valid_signature
        )

def test_reservation_overlap(blockchain_service, valid_wallet_address, valid_signature):
    """Testa criação de reservas com sobreposição de horário."""
    # Registrar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_service.register_station(station_data)
    
    # Criar primeira reserva
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_service.create_charging_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    # Tentar criar reserva com sobreposição
    with pytest.raises(ResourceConflictError):
        blockchain_service.create_charging_reservation(
            station.id,
            valid_wallet_address,
            start_time + timedelta(minutes=30),
            end_time + timedelta(minutes=30),
            valid_signature
        )

def test_blockchain_error(blockchain_service, web3):
    """Testa o tratamento de erro da blockchain."""
    # Desconectar o Web3 para simular erro
    web3.provider = None
    
    with pytest.raises(BlockchainError):
        blockchain_service.register_user("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    
    with pytest.raises(BlockchainError):
        blockchain_service.get_user_profile("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    
    with pytest.raises(BlockchainError):
        blockchain_service.get_station_details(1)
    
    with pytest.raises(BlockchainError):
        blockchain_service.get_session_details(1)
    
    with pytest.raises(BlockchainError):
        blockchain_service.get_reservation_details(1) 