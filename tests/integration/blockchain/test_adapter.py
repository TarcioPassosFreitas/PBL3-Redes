import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address

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
    return to_checksum_address(account.address)

@pytest.fixture
def valid_signature(web3, account):
    """Fixture que retorna uma assinatura válida para testes."""
    message = "Test message"
    message_hash = web3.keccak(text=message)
    signed_message = web3.eth.account.sign_message(message_hash, account.key)
    return signed_message.signature.hex()

def test_adapter_initialization(web3, contract_address):
    """Testa a inicialização do adaptador blockchain."""
    adapter = BlockchainAdapter(web3, contract_address)
    
    assert adapter.web3 is web3
    assert adapter.contract_address == contract_address
    assert adapter.contract is not None

def test_adapter_contract_connection(blockchain_adapter):
    """Testa a conexão com o contrato."""
    assert blockchain_adapter.contract.functions is not None
    assert blockchain_adapter.contract.events is not None

def test_adapter_transaction_building(blockchain_adapter, valid_wallet_address):
    """Testa a construção de transações."""
    # Criar usuário
    transaction = blockchain_adapter._build_transaction(
        blockchain_adapter.contract.functions.createUser(valid_wallet_address),
        valid_wallet_address
    )
    
    assert transaction["from"] == valid_wallet_address
    assert "nonce" in transaction
    assert "gas" in transaction
    assert "gasPrice" in transaction
    assert "data" in transaction

def test_adapter_transaction_signing(blockchain_adapter, web3, account):
    """Testa a assinatura de transações."""
    # Criar transação
    transaction = blockchain_adapter._build_transaction(
        blockchain_adapter.contract.functions.createUser(account.address),
        account.address
    )
    
    # Assinar transação
    signed_txn = blockchain_adapter._sign_transaction(transaction, account.key)
    
    assert signed_txn.rawTransaction is not None
    assert signed_txn.hash is not None
    assert signed_txn.r is not None
    assert signed_txn.s is not None
    assert signed_txn.v is not None

def test_adapter_transaction_sending(blockchain_adapter, web3, account):
    """Testa o envio de transações."""
    # Criar e assinar transação
    transaction = blockchain_adapter._build_transaction(
        blockchain_adapter.contract.functions.createUser(account.address),
        account.address
    )
    signed_txn = blockchain_adapter._sign_transaction(transaction, account.key)
    
    # Enviar transação
    tx_hash = blockchain_adapter._send_transaction(signed_txn)
    
    assert tx_hash is not None
    assert isinstance(tx_hash, bytes)
    
    # Aguardar confirmação
    receipt = blockchain_adapter._wait_for_transaction(tx_hash)
    
    assert receipt is not None
    assert receipt["status"] == 1
    assert receipt["contractAddress"] is None

def test_adapter_event_handling(blockchain_adapter, valid_wallet_address):
    """Testa o tratamento de eventos."""
    # Criar usuário para gerar evento
    blockchain_adapter.create_user(valid_wallet_address)
    
    # Obter eventos
    events = blockchain_adapter._get_events(
        blockchain_adapter.contract.events.UserCreated,
        from_block=0
    )
    
    assert len(events) > 0
    assert events[0]["args"]["walletAddress"] == valid_wallet_address

def test_adapter_error_handling(blockchain_adapter):
    """Testa o tratamento de erros."""
    # Testar erro de validação
    with pytest.raises(ValidationError):
        blockchain_adapter.create_user("invalid_address")
    
    # Testar erro de recurso não encontrado
    with pytest.raises(ResourceNotFoundError):
        blockchain_adapter.get_user("0x0000000000000000000000000000000000000000")
    
    # Testar erro de conflito
    with pytest.raises(ResourceConflictError):
        blockchain_adapter.create_station({
            "location": "Test Location",
            "power_output": -1,  # Valor inválido
            "price_per_kwh": 0.5,
            "owner_address": "0x0000000000000000000000000000000000000000"
        })
    
    # Testar erro da blockchain
    with pytest.raises(BlockchainError):
        blockchain_adapter.web3.provider = None
        blockchain_adapter.get_user("0x0000000000000000000000000000000000000000")

def test_adapter_gas_estimation(blockchain_adapter, valid_wallet_address):
    """Testa a estimativa de gas."""
    # Estimar gas para criar usuário
    gas_estimate = blockchain_adapter._estimate_gas(
        blockchain_adapter.contract.functions.createUser(valid_wallet_address),
        valid_wallet_address
    )
    
    assert gas_estimate > 0
    assert isinstance(gas_estimate, int)

def test_adapter_nonce_management(blockchain_adapter, valid_wallet_address):
    """Testa o gerenciamento de nonce."""
    # Obter nonce atual
    nonce = blockchain_adapter._get_nonce(valid_wallet_address)
    
    assert nonce >= 0
    assert isinstance(nonce, int)
    
    # Criar usuário para incrementar nonce
    blockchain_adapter.create_user(valid_wallet_address)
    
    # Verificar se nonce foi incrementado
    new_nonce = blockchain_adapter._get_nonce(valid_wallet_address)
    assert new_nonce > nonce

def test_adapter_balance_checking(blockchain_adapter, valid_wallet_address):
    """Testa a verificação de saldo."""
    # Verificar saldo
    balance = blockchain_adapter._get_balance(valid_wallet_address)
    
    assert balance >= 0
    assert isinstance(balance, int)

def test_adapter_contract_state_reading(blockchain_adapter, valid_wallet_address):
    """Testa a leitura do estado do contrato."""
    # Criar usuário
    blockchain_adapter.create_user(valid_wallet_address)
    
    # Ler estado do contrato
    user = blockchain_adapter._call_contract_function(
        blockchain_adapter.contract.functions.getUser(valid_wallet_address)
    )
    
    assert user is not None
    assert isinstance(user, dict)
    assert user["walletAddress"] == valid_wallet_address

def test_adapter_contract_state_writing(blockchain_adapter, valid_wallet_address):
    """Testa a escrita no estado do contrato."""
    # Criar estação
    station_data = {
        "location": "Test Location",
        "power_output": 50.0,
        "price_per_kwh": 0.5,
        "owner_address": valid_wallet_address
    }
    
    # Escrever no estado do contrato
    result = blockchain_adapter._send_contract_transaction(
        blockchain_adapter.contract.functions.createStation(
            station_data["location"],
            int(station_data["power_output"] * 100),  # Converter para centavos
            int(station_data["price_per_kwh"] * 100),  # Converter para centavos
            station_data["owner_address"]
        ),
        valid_wallet_address
    )
    
    assert result["success"] is True
    assert "station_id" in result["data"]

def test_adapter_transaction_receipt_parsing(blockchain_adapter, valid_wallet_address):
    """Testa o parsing de recibos de transação."""
    # Criar usuário
    result = blockchain_adapter.create_user(valid_wallet_address)
    
    # Verificar parsing do recibo
    assert "transaction_hash" in result
    assert "block_number" in result
    assert "gas_used" in result
    assert "status" in result

def test_adapter_event_parsing(blockchain_adapter, valid_wallet_address):
    """Testa o parsing de eventos."""
    # Criar usuário
    blockchain_adapter.create_user(valid_wallet_address)
    
    # Obter e verificar parsing de eventos
    events = blockchain_adapter._get_events(
        blockchain_adapter.contract.events.UserCreated,
        from_block=0
    )
    
    assert len(events) > 0
    event = events[0]
    assert "event" in event
    assert "args" in event
    assert "blockNumber" in event
    assert "transactionHash" in event

def test_adapter_error_parsing(blockchain_adapter):
    """Testa o parsing de erros."""
    # Testar erro de validação
    try:
        blockchain_adapter.create_user("invalid_address")
    except ValidationError as e:
        assert str(e) is not None
        assert "Invalid wallet address" in str(e)
    
    # Testar erro de recurso não encontrado
    try:
        blockchain_adapter.get_user("0x0000000000000000000000000000000000000000")
    except ResourceNotFoundError as e:
        assert str(e) is not None
        assert "User not found" in str(e)
    
    # Testar erro de conflito
    try:
        blockchain_adapter.create_station({
            "location": "Test Location",
            "power_output": -1,
            "price_per_kwh": 0.5,
            "owner_address": "0x0000000000000000000000000000000000000000"
        })
    except ResourceConflictError as e:
        assert str(e) is not None
        assert "Invalid power output" in str(e)

def test_adapter_retry_mechanism(blockchain_adapter, valid_wallet_address):
    """Testa o mecanismo de retry para transações."""
    # Simular falha temporária
    original_provider = blockchain_adapter.web3.provider
    blockchain_adapter.web3.provider = None
    
    try:
        # Tentar criar usuário (deve falhar)
        blockchain_adapter.create_user(valid_wallet_address)
    except BlockchainError:
        # Restaurar provider
        blockchain_adapter.web3.provider = original_provider
        
        # Tentar novamente (deve funcionar)
        result = blockchain_adapter.create_user(valid_wallet_address)
        assert result["success"] is True

def test_adapter_concurrent_transactions(blockchain_adapter, valid_wallet_address):
    """Testa o tratamento de transações concorrentes."""
    import asyncio
    
    async def create_user():
        return blockchain_adapter.create_user(valid_wallet_address)
    
    # Criar múltiplas transações concorrentes
    loop = asyncio.get_event_loop()
    tasks = [create_user() for _ in range(3)]
    
    # Executar transações
    results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    
    # Verificar resultados
    assert len(results) == 3
    assert all(isinstance(r, dict) for r in results if not isinstance(r, Exception))
    assert all(r["success"] is True for r in results if not isinstance(r, Exception))

def test_adapter_transaction_timeout(blockchain_adapter, valid_wallet_address):
    """Testa o timeout de transações."""
    # Configurar timeout curto
    blockchain_adapter.transaction_timeout = 1
    
    # Tentar transação que deve timeout
    with pytest.raises(BlockchainError) as e:
        blockchain_adapter.create_user(valid_wallet_address)
    
    assert "Transaction timeout" in str(e.value)

def test_adapter_gas_price_management(blockchain_adapter):
    """Testa o gerenciamento de preço de gas."""
    # Obter preço de gas
    gas_price = blockchain_adapter._get_gas_price()
    
    assert gas_price > 0
    assert isinstance(gas_price, int)
    
    # Verificar ajuste de preço de gas
    adjusted_price = blockchain_adapter._adjust_gas_price(gas_price)
    
    assert adjusted_price >= gas_price
    assert isinstance(adjusted_price, int)

def test_adapter_block_confirmation(blockchain_adapter, valid_wallet_address):
    """Testa a confirmação de blocos."""
    # Criar usuário
    result = blockchain_adapter.create_user(valid_wallet_address)
    
    # Aguardar confirmações
    confirmations = blockchain_adapter._wait_for_confirmations(
        result["transaction_hash"],
        confirmations=2
    )
    
    assert confirmations >= 2

def test_adapter_contract_upgrade(blockchain_adapter, web3, account):
    """Testa a atualização do contrato."""
    # Compilar novo contrato
    with open("contracts/EVChargingV2.sol", "r") as f:
        new_contract_source = f.read()
    
    # Deploy do novo contrato
    new_contract = web3.eth.contract(
        abi=new_contract_abi,  # ABI do novo contrato
        bytecode=new_contract_bytecode  # Bytecode do novo contrato
    )
    
    # Construir transação de upgrade
    transaction = new_contract.constructor().build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": 2000000,
        "gasPrice": web3.eth.gas_price
    })
    
    # Assinar e enviar transação
    signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Atualizar adaptador
    blockchain_adapter.update_contract(tx_receipt.contractAddress)
    
    # Verificar atualização
    assert blockchain_adapter.contract_address == tx_receipt.contractAddress
    assert blockchain_adapter.contract is not None
    assert blockchain_adapter.contract.functions is not None
    assert blockchain_adapter.contract.events is not None 