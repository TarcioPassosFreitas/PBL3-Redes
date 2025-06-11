import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from web3 import Web3
from eth_account import Account

from adapters.blockchain.blockchain_adapter import BlockchainAdapter
from domain.entities.session import SessionStatus
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
def valid_wallet_address(account):
    """Fixture que retorna um endereço de carteira válido para testes."""
    return account.address

@pytest.fixture
def valid_signature(web3, account):
    """Fixture que retorna uma assinatura válida para testes."""
    message = "Test message"
    message_hash = web3.keccak(text=message)
    signed_message = web3.eth.account.sign_message(message_hash, account.key)
    return signed_message.signature.hex()

def test_create_user(blockchain_adapter, valid_wallet_address):
    """Testa a criação de um usuário no contrato."""
    result = blockchain_adapter.create_user(valid_wallet_address)
    
    assert result["success"] is True
    assert result["data"]["wallet_address"] == valid_wallet_address
    
    # Verificar se o usuário foi criado
    user = blockchain_adapter.get_user(valid_wallet_address)
    assert user["wallet_address"] == valid_wallet_address
    assert user["total_charges"] == 0
    assert len(user["active_sessions"]) == 0
    assert len(user["active_reservations"]) == 0

def test_create_station(blockchain_adapter, valid_wallet_address):
    """Testa a criação de uma estação no contrato."""
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    
    result = blockchain_adapter.create_station(station_data)
    
    assert result["success"] is True
    assert "station_id" in result["data"]
    
    # Verificar se a estação foi criada
    station = blockchain_adapter.get_station(result["data"]["station_id"])
    assert station["location"] == station_data["location"]
    assert station["power_output"] == station_data["power_output"]
    assert station["price_per_kwh"] == station_data["price_per_kwh"]
    assert station["owner_address"] == station_data["owner_address"]
    assert station["is_available"] is True
    assert station["total_revenue"] == 0

def test_start_session(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa o início de uma sessão no contrato."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    # Iniciar sessão
    result = blockchain_adapter.start_session(
        station_id,
        valid_wallet_address,
        valid_signature
    )
    
    assert result["success"] is True
    assert "session_id" in result["data"]
    
    # Verificar se a sessão foi criada
    session = blockchain_adapter.get_session(result["data"]["session_id"])
    assert session["station_id"] == station_id
    assert session["wallet_address"] == valid_wallet_address
    assert session["status"] == SessionStatus.ACTIVE.value
    assert "start_time" in session
    
    # Verificar se a estação está ocupada
    station = blockchain_adapter.get_station(station_id)
    assert station["is_available"] is False
    assert station["current_session_id"] == result["data"]["session_id"]

def test_end_session(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa o fim de uma sessão no contrato."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    session_result = blockchain_adapter.start_session(
        station_id,
        valid_wallet_address,
        valid_signature
    )
    session_id = session_result["data"]["session_id"]
    
    # Finalizar sessão
    result = blockchain_adapter.end_session(session_id)
    
    assert result["success"] is True
    assert result["data"]["session_id"] == session_id
    assert result["data"]["status"] == SessionStatus.COMPLETED.value
    
    # Verificar se a sessão foi finalizada
    session = blockchain_adapter.get_session(session_id)
    assert session["status"] == SessionStatus.COMPLETED.value
    assert "end_time" in session
    
    # Verificar se a estação está disponível
    station = blockchain_adapter.get_station(station_id)
    assert station["is_available"] is True
    assert station["current_session_id"] is None

def test_process_payment(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa o processamento de um pagamento no contrato."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    session_result = blockchain_adapter.start_session(
        station_id,
        valid_wallet_address,
        valid_signature
    )
    session_id = session_result["data"]["session_id"]
    
    # Finalizar sessão
    blockchain_adapter.end_session(session_id)
    
    # Processar pagamento
    result = blockchain_adapter.process_payment(
        session_id,
        valid_wallet_address,
        valid_signature
    )
    
    assert result["success"] is True
    assert result["data"]["session_id"] == session_id
    assert result["data"]["status"] == SessionStatus.PAID.value
    assert "payment_amount" in result["data"]
    assert "payment_time" in result["data"]
    
    # Verificar se a sessão foi paga
    session = blockchain_adapter.get_session(session_id)
    assert session["status"] == SessionStatus.PAID.value
    assert "payment_amount" in session
    assert "payment_time" in session
    
    # Verificar se a estação recebeu o pagamento
    station = blockchain_adapter.get_station(station_id)
    assert station["total_revenue"] > 0

def test_create_reservation(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa a criação de uma reserva no contrato."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    # Criar reserva
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    result = blockchain_adapter.create_reservation(
        station_id,
        valid_wallet_address,
        start_time.isoformat(),
        end_time.isoformat(),
        valid_signature
    )
    
    assert result["success"] is True
    assert "reservation_id" in result["data"]
    
    # Verificar se a reserva foi criada
    reservation = blockchain_adapter.get_reservation(result["data"]["reservation_id"])
    assert reservation["station_id"] == station_id
    assert reservation["wallet_address"] == valid_wallet_address
    assert reservation["start_time"] == start_time.isoformat()
    assert reservation["end_time"] == end_time.isoformat()

def test_cancel_reservation(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa o cancelamento de uma reserva no contrato."""
    # Criar estação e reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    reservation_result = blockchain_adapter.create_reservation(
        station_id,
        valid_wallet_address,
        start_time.isoformat(),
        end_time.isoformat(),
        valid_signature
    )
    reservation_id = reservation_result["data"]["reservation_id"]
    
    # Cancelar reserva
    result = blockchain_adapter.cancel_reservation(
        reservation_id,
        valid_wallet_address,
        valid_signature
    )
    
    assert result["success"] is True
    assert result["data"]["reservation_id"] == reservation_id
    assert result["data"]["status"] == "cancelled"
    
    # Verificar se a reserva foi cancelada
    reservation = blockchain_adapter.get_reservation(reservation_id)
    assert reservation["status"] == "cancelled"

def test_get_user_sessions(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa a obtenção das sessões de um usuário no contrato."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    session_result = blockchain_adapter.start_session(
        station_id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter sessões do usuário
    result = blockchain_adapter.get_user_sessions(valid_wallet_address)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(session, dict) for session in result)
    assert all("session_id" in session for session in result)
    assert all("station_id" in session for session in result)
    assert all("status" in session for session in result)

def test_get_station_sessions(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa a obtenção das sessões de uma estação no contrato."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    blockchain_adapter.start_session(
        station_id,
        valid_wallet_address,
        valid_signature
    )
    
    # Obter sessões da estação
    result = blockchain_adapter.get_station_sessions(station_id)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(session, dict) for session in result)
    assert all("session_id" in session for session in result)
    assert all("wallet_address" in session for session in result)
    assert all("status" in session for session in result)

def test_get_user_reservations(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa a obtenção das reservas de um usuário no contrato."""
    # Criar estação e reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_adapter.create_reservation(
        station_id,
        valid_wallet_address,
        start_time.isoformat(),
        end_time.isoformat(),
        valid_signature
    )
    
    # Obter reservas do usuário
    result = blockchain_adapter.get_user_reservations(valid_wallet_address)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(reservation, dict) for reservation in result)
    assert all("reservation_id" in reservation for reservation in result)
    assert all("station_id" in reservation for reservation in result)
    assert all("start_time" in reservation for reservation in result)
    assert all("end_time" in reservation for reservation in result)

def test_get_station_reservations(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa a obtenção das reservas de uma estação no contrato."""
    # Criar estação e reserva
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_adapter.create_reservation(
        station_id,
        valid_wallet_address,
        start_time.isoformat(),
        end_time.isoformat(),
        valid_signature
    )
    
    # Obter reservas da estação
    result = blockchain_adapter.get_station_reservations(station_id)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(reservation, dict) for reservation in result)
    assert all("reservation_id" in reservation for reservation in result)
    assert all("wallet_address" in reservation for reservation in result)
    assert all("start_time" in reservation for reservation in result)
    assert all("end_time" in reservation for reservation in result)

def test_invalid_wallet_address(blockchain_adapter):
    """Testa operações com endereço de carteira inválido."""
    invalid_wallet = "0x0000000000000000000000000000000000000000"
    
    with pytest.raises(ValidationError):
        blockchain_adapter.create_user(invalid_wallet)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_user(invalid_wallet)

def test_invalid_station_id(blockchain_adapter):
    """Testa operações com ID de estação inválido."""
    invalid_station_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_station(invalid_station_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_station_sessions(invalid_station_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_station_reservations(invalid_station_id)

def test_invalid_session_id(blockchain_adapter):
    """Testa operações com ID de sessão inválido."""
    invalid_session_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_session(invalid_session_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.end_session(invalid_session_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.process_payment(
            invalid_session_id,
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"
        )

def test_invalid_reservation_id(blockchain_adapter):
    """Testa operações com ID de reserva inválido."""
    invalid_reservation_id = 999
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_reservation(invalid_reservation_id)
    
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.cancel_reservation(
            invalid_reservation_id,
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"
        )

def test_station_busy(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa operações em estação ocupada."""
    # Criar estação e iniciar sessão
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    blockchain_adapter.start_session(
        station_id,
        valid_wallet_address,
        valid_signature
    )
    
    # Tentar iniciar outra sessão
    with pytest.raises(ResourceConflictError):
        blockchain_adapter.start_session(
            station_id,
            valid_wallet_address,
            valid_signature
        )

def test_reservation_overlap(blockchain_adapter, valid_wallet_address, valid_signature):
    """Testa criação de reservas com sobreposição de horário."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    station_result = blockchain_adapter.create_station(station_data)
    station_id = station_result["data"]["station_id"]
    
    # Criar primeira reserva
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    blockchain_adapter.create_reservation(
        station_id,
        valid_wallet_address,
        start_time.isoformat(),
        end_time.isoformat(),
        valid_signature
    )
    
    # Tentar criar reserva com sobreposição
    with pytest.raises(ResourceConflictError):
        blockchain_adapter.create_reservation(
            station_id,
            valid_wallet_address,
            (start_time + timedelta(minutes=30)).isoformat(),
            (end_time + timedelta(minutes=30)).isoformat(),
            valid_signature
        )

def test_blockchain_error(blockchain_adapter, web3):
    """Testa o tratamento de erro da blockchain."""
    # Desconectar o Web3 para simular erro
    web3.provider = None
    
    with pytest.raises(BlockchainError):
        blockchain_adapter.create_user("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    
    with pytest.raises(BlockchainError):
        blockchain_adapter.get_user("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    
    with pytest.raises(BlockchainError):
        blockchain_adapter.get_station(1)
    
    with pytest.raises(BlockchainError):
        blockchain_adapter.get_session(1)
    
    with pytest.raises(BlockchainError):
        blockchain_adapter.get_reservation(1) 