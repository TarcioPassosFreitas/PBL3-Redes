import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address

from adapters.blockchain.blockchain_adapter import BlockchainAdapter
from repositories.blockchain_repository import BlockchainRepository
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

def test_create_user(blockchain_repository, valid_wallet_address):
    """Testa a criação de um usuário."""
    user = blockchain_repository.create_user(valid_wallet_address)
    
    assert isinstance(user, User)
    assert user.wallet_address == valid_wallet_address
    assert user.total_charges == 0
    assert len(user.active_sessions) == 0
    assert len(user.active_reservations) == 0

def test_get_user(blockchain_repository, valid_wallet_address):
    """Testa a obtenção de um usuário."""
    # Criar usuário
    blockchain_repository.create_user(valid_wallet_address)
    
    # Obter usuário
    user = blockchain_repository.get_user(valid_wallet_address)
    
    assert isinstance(user, User)
    assert user.wallet_address == valid_wallet_address
    assert user.total_charges == 0
    assert len(user.active_sessions) == 0
    assert len(user.active_reservations) == 0

def test_create_station(blockchain_repository, valid_wallet_address):
    """Testa a criação de uma estação."""
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    
    station = blockchain_repository.create_station(station_data)
    
    assert isinstance(station, Station)
    assert station.location == station_data["location"]
    assert station.power_output == station_data["power_output"]
    assert station.price_per_kwh == station_data["price_per_kwh"]
    assert station.owner_address == station_data["owner_address"]
    assert station.is_available is True
    assert station.total_revenue == 0

def test_get_station(blockchain_repository, valid_wallet_address):
    """Testa a obtenção de uma estação."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    created_station = blockchain_repository.create_station(station_data)
    
    # Obter estação
    station = blockchain_repository.get_station(created_station.id)
    
    assert isinstance(station, Station)
    assert station.id == created_station.id
    assert station.location == station_data["location"]
    assert station.power_output == station_data["power_output"]
    assert station.price_per_kwh == station_data["price_per_kwh"]
    assert station.owner_address == station_data["owner_address"]
    assert station.is_available is True
    assert station.total_revenue == 0

def test_start_session(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa o início de uma sessão."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    # Iniciar sessão
    session = blockchain_repository.start_session(
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

def test_end_session(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa o fim de uma sessão."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    session = blockchain_repository.start_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Finalizar sessão
    ended_session = blockchain_repository.end_session(session.id)
    
    assert ended_session.id == session.id
    assert ended_session.status == SessionStatus.COMPLETED
    assert ended_session.end_time is not None
    assert ended_session.payment_amount is None
    assert ended_session.payment_time is None

def test_process_payment(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa o processamento de um pagamento."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    session = blockchain_repository.start_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Finalizar sessão
    blockchain_repository.end_session(session.id)
    
    # Processar pagamento
    paid_session = blockchain_repository.process_payment(
        session.id,
        valid_wallet_address,
        valid_signature
    )
    
    assert paid_session.id == session.id
    assert paid_session.status == SessionStatus.PAID
    assert paid_session.payment_amount is not None
    assert paid_session.payment_time is not None

def test_create_reservation(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa a criação de uma reserva."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    # Criar reserva
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    reservation = blockchain_repository.create_reservation(
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

def test_cancel_reservation(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa o cancelamento de uma reserva."""
    # Criar estação e reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    reservation = blockchain_repository.create_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    # Cancelar reserva
    cancelled_reservation = blockchain_repository.cancel_reservation(
        reservation.id,
        valid_wallet_address,
        valid_signature
    )
    
    assert cancelled_reservation.id == reservation.id
    assert cancelled_reservation.status == "cancelled"

def test_get_user_sessions(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa a obtenção das sessões de um usuário."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    blockchain_repository.start_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter sessões do usuário
    sessions = blockchain_repository.get_user_sessions(valid_wallet_address)
    
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    assert all(isinstance(session, Session) for session in sessions)
    assert all(session.wallet_address == valid_wallet_address for session in sessions)

def test_get_station_sessions(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa a obtenção das sessões de uma estação."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    blockchain_repository.start_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter sessões da estação
    sessions = blockchain_repository.get_station_sessions(station.id)
    
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    assert all(isinstance(session, Session) for session in sessions)
    assert all(session.station_id == station.id for session in sessions)

def test_get_user_reservations(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa a obtenção das reservas de um usuário."""
    # Criar estação e reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_repository.create_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    # Obter reservas do usuário
    reservations = blockchain_repository.get_user_reservations(valid_wallet_address)
    
    assert isinstance(reservations, list)
    assert len(reservations) > 0
    assert all(isinstance(reservation, Reservation) for reservation in reservations)
    assert all(reservation.wallet_address == valid_wallet_address for reservation in reservations)

def test_get_station_reservations(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa a obtenção das reservas de uma estação."""
    # Criar estação e reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_repository.create_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    # Obter reservas da estação
    reservations = blockchain_repository.get_station_reservations(station.id)
    
    assert isinstance(reservations, list)
    assert len(reservations) > 0
    assert all(isinstance(reservation, Reservation) for reservation in reservations)
    assert all(reservation.station_id == station.id for reservation in reservations)

def test_invalid_wallet_address(blockchain_repository):
    """Testa operações com endereço de carteira inválido."""
    invalid_wallet = "0x0000000000000000000000000000000000000000"
    
    with pytest.raises(ValidationError):
        blockchain_repository.create_user(invalid_wallet)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.get_user(invalid_wallet)

def test_invalid_station_id(blockchain_repository):
    """Testa operações com ID de estação inválido."""
    invalid_station_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.get_station(invalid_station_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.get_station_sessions(invalid_station_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.get_station_reservations(invalid_station_id)

def test_invalid_session_id(blockchain_repository):
    """Testa operações com ID de sessão inválido."""
    invalid_session_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.get_session(invalid_session_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.end_session(invalid_session_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.process_payment(
            invalid_session_id,
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"
        )

def test_invalid_reservation_id(blockchain_repository):
    """Testa operações com ID de reserva inválido."""
    invalid_reservation_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.get_reservation(invalid_reservation_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_repository.cancel_reservation(
            invalid_reservation_id,
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"
        )

def test_station_busy(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa operações em estação ocupada."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    blockchain_repository.start_session(
        station.id,
        valid_wallet_address,
        valid_signature
    )
    
    # Tentar iniciar outra sessão
    with pytest.raises(ResourceConflictError):
        blockchain_repository.start_session(
            station.id,
            valid_wallet_address,
            valid_signature
        )

def test_reservation_overlap(blockchain_repository, valid_wallet_address, valid_signature):
    """Testa criação de reservas com sobreposição de horário."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station = blockchain_repository.create_station(station_data)
    
    # Criar primeira reserva
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_repository.create_reservation(
        station.id,
        valid_wallet_address,
        start_time,
        end_time,
        valid_signature
    )
    
    # Tentar criar reserva com sobreposição
    with pytest.raises(ResourceConflictError):
        blockchain_repository.create_reservation(
            station.id,
            valid_wallet_address,
            start_time + timedelta(minutes=30),
            end_time + timedelta(minutes=30),
            valid_signature
        )

def test_blockchain_error(blockchain_repository, web3):
    """Testa o tratamento de erro da blockchain."""
    # Desconectar o Web3 para simular erro
    web3.provider = None
    
    with pytest.raises(BlockchainError):
        blockchain_repository.create_user("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    
    with pytest.raises(BlockchainError):
        blockchain_repository.get_user("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    
    with pytest.raises(BlockchainError):
        blockchain_repository.get_station(1)
    
    with pytest.raises(BlockchainError):
        blockchain_repository.get_session(1)
    
    with pytest.raises(BlockchainError):
        blockchain_repository.get_reservation(1) 