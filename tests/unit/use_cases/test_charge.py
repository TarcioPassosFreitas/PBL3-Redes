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
async def test_start_session_success(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_session_data):
    """Testa o início bem-sucedido de uma sessão."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_blockchain_port.get_station.return_value = mock_station()
    mock_blockchain_port.get_user.return_value = mock_user()
    
    # Executar caso de uso
    result = await mock_charge_use_case.start_session(
        valid_session_data["station_id"],
        valid_session_data["wallet_address"],
        valid_session_data["signature"]
    )
    
    # Verificar resultado
    assert result["success"] is True
    assert "session_id" in result["data"]
    assert result["data"]["status"] == SessionStatus.ACTIVE.value
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_session_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_station.assert_called_once_with(valid_session_data["station_id"])
    mock_blockchain_port.get_user.assert_called_once_with(valid_session_data["wallet_address"])

@pytest.mark.asyncio
async def test_end_session_success(mock_charge_use_case, mock_http_port, mock_blockchain_port):
    """Testa o fim bem-sucedido de uma sessão."""
    session_id = 1
    mock_session = mock_session()
    mock_session.start(datetime.utcnow())
    
    # Configurar mocks
    mock_blockchain_port.get_session.return_value = mock_session
    
    # Executar caso de uso
    result = await mock_charge_use_case.end_session(session_id)
    
    # Verificar resultado
    assert result["success"] is True
    assert result["data"]["session_id"] == session_id
    assert result["data"]["status"] == SessionStatus.COMPLETED.value
    
    # Verificar chamadas aos mocks
    mock_blockchain_port.get_session.assert_called_once_with(session_id)

@pytest.mark.asyncio
async def test_get_user_sessions_success(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_wallet_address):
    """Testa a obtenção bem-sucedida das sessões de um usuário."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_blockchain_port.get_user.return_value = mock_user()
    mock_blockchain_port.get_session.side_effect = [
        mock_session(),
        mock_session()
    ]
    
    # Executar caso de uso
    result = await mock_charge_use_case.get_user_sessions(valid_wallet_address)
    
    # Verificar resultado
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(session, dict) for session in result)
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_wallet_address)
    mock_blockchain_port.get_user.assert_called_once_with(valid_wallet_address)

@pytest.mark.asyncio
async def test_get_station_sessions_success(mock_charge_use_case, mock_http_port, mock_blockchain_port):
    """Testa a obtenção bem-sucedida das sessões de uma estação."""
    station_id = 1
    
    # Configurar mocks
    mock_blockchain_port.get_station.return_value = mock_station()
    mock_blockchain_port.get_session.side_effect = [
        mock_session(),
        mock_session()
    ]
    
    # Executar caso de uso
    result = await mock_charge_use_case.get_station_sessions(station_id)
    
    # Verificar resultado
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(session, dict) for session in result)
    
    # Verificar chamadas aos mocks
    mock_blockchain_port.get_station.assert_called_once_with(station_id)

@pytest.mark.asyncio
async def test_start_session_invalid_wallet(mock_charge_use_case, mock_http_port, valid_session_data):
    """Testa o início de sessão com carteira inválida."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = False
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ValidationError):
        await mock_charge_use_case.start_session(
            valid_session_data["station_id"],
            valid_session_data["wallet_address"],
            valid_session_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_session_data["wallet_address"])

@pytest.mark.asyncio
async def test_start_session_invalid_signature(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_session_data):
    """Testa o início de sessão com assinatura inválida."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = False
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ValidationError):
        await mock_charge_use_case.start_session(
            valid_session_data["station_id"],
            valid_session_data["wallet_address"],
            valid_session_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_session_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()

@pytest.mark.asyncio
async def test_start_session_station_not_found(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_session_data):
    """Testa o início de sessão com estação inexistente."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_blockchain_port.get_station.side_effect = ResourceNotFoundError(valid_session_data["station_id"])
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceNotFoundError):
        await mock_charge_use_case.start_session(
            valid_session_data["station_id"],
            valid_session_data["wallet_address"],
            valid_session_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_session_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_station.assert_called_once_with(valid_session_data["station_id"])

@pytest.mark.asyncio
async def test_start_session_station_busy(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_session_data):
    """Testa o início de sessão em estação ocupada."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    station = mock_station()
    station.start_session(1)  # Marcar estação como ocupada
    mock_blockchain_port.get_station.return_value = station
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceConflictError):
        await mock_charge_use_case.start_session(
            valid_session_data["station_id"],
            valid_session_data["wallet_address"],
            valid_session_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_session_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_station.assert_called_once_with(valid_session_data["station_id"])

@pytest.mark.asyncio
async def test_end_session_not_found(mock_charge_use_case, mock_blockchain_port):
    """Testa o fim de uma sessão inexistente."""
    session_id = 999
    
    # Configurar mocks
    mock_blockchain_port.get_session.side_effect = ResourceNotFoundError(session_id)
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceNotFoundError):
        await mock_charge_use_case.end_session(session_id)
    
    # Verificar chamadas aos mocks
    mock_blockchain_port.get_session.assert_called_once_with(session_id)

@pytest.mark.asyncio
async def test_end_session_already_ended(mock_charge_use_case, mock_blockchain_port):
    """Testa o fim de uma sessão já finalizada."""
    session_id = 1
    mock_session = mock_session()
    mock_session.start(datetime.utcnow())
    mock_session.end(datetime.utcnow() + timedelta(hours=2))
    
    # Configurar mocks
    mock_blockchain_port.get_session.return_value = mock_session
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ValidationError):
        await mock_charge_use_case.end_session(session_id)
    
    # Verificar chamadas aos mocks
    mock_blockchain_port.get_session.assert_called_once_with(session_id)

@pytest.mark.asyncio
async def test_get_user_sessions_user_not_found(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_wallet_address):
    """Testa a obtenção de sessões de um usuário inexistente."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_blockchain_port.get_user.side_effect = ResourceNotFoundError(valid_wallet_address)
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceNotFoundError):
        await mock_charge_use_case.get_user_sessions(valid_wallet_address)
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_wallet_address)
    mock_blockchain_port.get_user.assert_called_once_with(valid_wallet_address)

@pytest.mark.asyncio
async def test_get_station_sessions_station_not_found(mock_charge_use_case, mock_blockchain_port):
    """Testa a obtenção de sessões de uma estação inexistente."""
    station_id = 999
    
    # Configurar mocks
    mock_blockchain_port.get_station.side_effect = ResourceNotFoundError(station_id)
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(ResourceNotFoundError):
        await mock_charge_use_case.get_station_sessions(station_id)
    
    # Verificar chamadas aos mocks
    mock_blockchain_port.get_station.assert_called_once_with(station_id)

@pytest.mark.asyncio
async def test_blockchain_error(mock_charge_use_case, mock_http_port, mock_blockchain_port, valid_session_data):
    """Testa o tratamento de erro da blockchain."""
    # Configurar mocks
    mock_http_port.validate_wallet_address.return_value = True
    mock_http_port.validate_signature.return_value = True
    mock_blockchain_port.get_station.side_effect = BlockchainError("Erro na blockchain")
    
    # Executar caso de uso e verificar exceção
    with pytest.raises(BlockchainError):
        await mock_charge_use_case.start_session(
            valid_session_data["station_id"],
            valid_session_data["wallet_address"],
            valid_session_data["signature"]
        )
    
    # Verificar chamadas aos mocks
    mock_http_port.validate_wallet_address.assert_called_once_with(valid_session_data["wallet_address"])
    mock_http_port.validate_signature.assert_called_once()
    mock_blockchain_port.get_station.assert_called_once_with(valid_session_data["station_id"]) 