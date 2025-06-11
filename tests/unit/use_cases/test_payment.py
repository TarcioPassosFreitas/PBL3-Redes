import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from domain.entities.session import SessionStatus
from domain.exceptions.custom_exceptions import (
    ValidationError,
    ResourceNotFoundError,
    ResourceConflictError,
    BlockchainError
)

@pytest.mark.asyncio
async def test_process_payment_success(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_payment_data):
    """Testa o processamento bem-sucedido de um pagamento."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_session = mock_session()
    mock_session.start(datetime.utcnow())
    mock_session.end(datetime.utcnow() + timedelta(hours=2))
    mock_blockchain_port.get_session.return_value = mock_session
    mock_blockchain_port.get_user.return_value = mock_user()
    
    # Executar caso de uso
    result = await mock_payment_use_case.process_payment(
        valid_payment_data["session_id"],
        valid_payment_data["wallet_address"],
        valid_payment_data["signature"]
    )
    
    # Verificar resultado
    assert result["success"] is True
    assert result["data"]["session_id"] == valid_payment_data["session_id"]
    assert result["data"]["status"] == SessionStatus.PAID.value
    assert "payment_amount" in result["data"]
    assert "payment_time" in result["data"]
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_session.assert_called_once_with(valid_payment_data["session_id"])
    mock_blockchain_port.get_user.assert_called_once_with(valid_payment_data["wallet_address"])

@pytest.mark.asyncio
async def test_get_payment_history_success(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_wallet_address):
    """Testa a obtenção bem-sucedida do histórico de pagamentos."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_blockchain_port.get_user.return_value = mock_user()
    mock_blockchain_port.get_session.side_effect = [
        mock_session(),
        mock_session()
    ]
    
    # Executar caso de uso
    result = await mock_payment_use_case.get_payment_history(valid_wallet_address)
    
    # Verificar resultado
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(payment, dict) for payment in result)
    assert all("session_id" in payment for payment in result)
    assert all("payment_amount" in payment for payment in result)
    assert all("payment_time" in payment for payment in result)
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_wallet_address)
    mock_blockchain_port.get_user.assert_called_once_with(valid_wallet_address)

@pytest.mark.asyncio
async def test_process_payment_invalid_wallet(mock_payment_use_case, mock_http_port, valid_payment_data):
    """Testa o processamento de pagamento com carteira inválida."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = False
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ValidationError):
        await mock_payment_use_case.process_payment(
            valid_payment_data["session_id"],
            valid_payment_data["wallet_address"],
            valid_payment_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])

@pytest.mark.asyncio
async def test_process_payment_invalid_signature(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_payment_data):
    """Testa o processamento de pagamento com assinatura inválida."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = False
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ValidationError):
        await mock_payment_use_case.process_payment(
            valid_payment_data["session_id"],
            valid_payment_data["wallet_address"],
            valid_payment_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()

@pytest.mark.asyncio
async def test_process_payment_session_not_found(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_payment_data):
    """Testa o processamento de pagamento para sessão inexistente."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_blockchain_port.get_session.side_effect = ResourceNotFoundError(valid_payment_data["session_id"])
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceNotFoundError):
        await mock_payment_use_case.process_payment(
            valid_payment_data["session_id"],
            valid_payment_data["wallet_address"],
            valid_payment_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_session.assert_called_once_with(valid_payment_data["session_id"])

@pytest.mark.asyncio
async def test_process_payment_session_not_ended(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_payment_data):
    """Testa o processamento de pagamento para sessão não finalizada."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_session = mock_session()
    mock_session.start(datetime.utcnow())  # Sessão ativa, não finalizada
    mock_blockchain_port.get_session.return_value = mock_session
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ValidationError):
        await mock_payment_use_case.process_payment(
            valid_payment_data["session_id"],
            valid_payment_data["wallet_address"],
            valid_payment_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_session.assert_called_once_with(valid_payment_data["session_id"])

@pytest.mark.asyncio
async def test_process_payment_already_paid(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_payment_data):
    """Testa o processamento de pagamento para sessão já paga."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_session = mock_session()
    mock_session.start(datetime.utcnow())
    mock_session.end(datetime.utcnow() + timedelta(hours=2))
    mock_session.pay(Decimal("50.00"), datetime.utcnow())  # Marcar como paga
    mock_blockchain_port.get_session.return_value = mock_session
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceConflictError):
        await mock_payment_use_case.process_payment(
            valid_payment_data["session_id"],
            valid_payment_data["wallet_address"],
            valid_payment_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_session.assert_called_once_with(valid_payment_data["session_id"])

@pytest.mark.asyncio
async def test_get_payment_history_user_not_found(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_wallet_address):
    """Testa a obtenção de histórico de pagamentos para usuário inexistente."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_blockchain_port.get_user.side_effect = ResourceNotFoundError(valid_wallet_address)
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceNotFoundError):
        await mock_payment_use_case.get_payment_history(valid_wallet_address)
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_wallet_address)
    mock_blockchain_port.get_user.assert_called_once_with(valid_wallet_address)

@pytest.mark.asyncio
async def test_blockchain_error(mock_payment_use_case, mock_http_port, mock_blockchain_port, valid_payment_data):
    """Testa o tratamento de erro da blockchain."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_blockchain_port.get_session.side_effect = BlockchainError("Erro na blockchain")
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(BlockchainError):
        await mock_payment_use_case.process_payment(
            valid_payment_data["session_id"],
            valid_payment_data["wallet_address"],
            valid_payment_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_payment_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_session.assert_called_once_with(valid_payment_data["session_id"]) 