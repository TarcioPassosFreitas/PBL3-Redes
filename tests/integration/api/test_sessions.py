import pytest
from datetime import datetime, timedelta
import json

from app import create_app
from domain.entities.session import SessionStatus

@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação para testes."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "BLOCKCHAIN_NETWORK": "test",
        "BLOCKCHAIN_CONTRACT_ADDRESS": "0x0000000000000000000000000000000000000000"
    })
    return app

@pytest.fixture
def client(app):
    """Fixture que cria um cliente de teste."""
    return app.test_client()

@pytest.fixture
def valid_wallet_address():
    """Fixture que retorna um endereço de carteira válido para testes."""
    return "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

@pytest.fixture
def valid_signature():
    """Fixture que retorna uma assinatura válida para testes."""
    return "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"

@pytest.fixture
def valid_session_data(valid_wallet_address, valid_signature):
    """Fixture que retorna dados válidos para uma sessão."""
    return {
        "station_id": 1,
        "wallet_address": valid_wallet_address,
        "signature": valid_signature
    }

def test_start_session_success(client, valid_session_data):
    """Testa o início bem-sucedido de uma sessão via API."""
    response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert "session_id" in data["data"]
    assert data["data"]["station_id"] == valid_session_data["station_id"]
    assert data["data"]["wallet_address"] == valid_session_data["wallet_address"]
    assert data["data"]["status"] == SessionStatus.ACTIVE.value

def test_start_session_invalid_data(client):
    """Testa o início de sessão com dados inválidos."""
    invalid_data = {
        "station_id": "invalid",
        "wallet_address": "invalid",
        "signature": "invalid"
    }
    
    response = client.post(
        "/api/v1/sessions",
        data=json.dumps(invalid_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_start_session_missing_data(client):
    """Testa o início de sessão com dados faltando."""
    incomplete_data = {
        "station_id": 1,
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }
    
    response = client.post(
        "/api/v1/sessions",
        data=json.dumps(incomplete_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_end_session_success(client, valid_session_data):
    """Testa o fim bem-sucedido de uma sessão via API."""
    # Primeiro inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Depois finaliza a sessão
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    
    assert end_response.status_code == 200
    data = json.loads(end_response.data)
    assert data["success"] is True
    assert data["data"]["session_id"] == session_id
    assert data["data"]["status"] == SessionStatus.COMPLETED.value

def test_end_session_not_found(client):
    """Testa o fim de uma sessão inexistente."""
    session_id = 999
    response = client.post(f"/api/v1/sessions/{session_id}/end")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_end_session_already_ended(client, valid_session_data):
    """Testa o fim de uma sessão já finalizada."""
    # Primeiro inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Finaliza a sessão pela primeira vez
    end_response1 = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response1.status_code == 200
    
    # Tenta finalizar novamente
    end_response2 = client.post(f"/api/v1/sessions/{session_id}/end")
    
    assert end_response2.status_code == 400
    data = json.loads(end_response2.data)
    assert data["success"] is False
    assert "error" in data

def test_get_user_sessions_success(client, valid_wallet_address):
    """Testa a obtenção bem-sucedida das sessões de um usuário via API."""
    response = client.get(f"/api/v1/users/{valid_wallet_address}/sessions")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all(isinstance(session, dict) for session in data)
    assert all("session_id" in session for session in data)
    assert all("station_id" in session for session in data)
    assert all("status" in session for session in data)

def test_get_user_sessions_not_found(client):
    """Testa a obtenção de sessões de um usuário inexistente."""
    invalid_wallet = "0x0000000000000000000000000000000000000000"
    response = client.get(f"/api/v1/users/{invalid_wallet}/sessions")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_get_station_sessions_success(client):
    """Testa a obtenção bem-sucedida das sessões de uma estação via API."""
    station_id = 1
    response = client.get(f"/api/v1/stations/{station_id}/sessions")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all(isinstance(session, dict) for session in data)
    assert all("session_id" in session for session in data)
    assert all("wallet_address" in session for session in data)
    assert all("status" in session for session in data)

def test_get_station_sessions_not_found(client):
    """Testa a obtenção de sessões de uma estação inexistente."""
    station_id = 999
    response = client.get(f"/api/v1/stations/{station_id}/sessions")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_start_session_station_busy(client, valid_session_data):
    """Testa o início de sessão em estação ocupada."""
    # Primeiro inicia uma sessão
    response1 = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert response1.status_code == 201
    
    # Tenta iniciar outra sessão na mesma estação
    response2 = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    
    assert response2.status_code == 409
    data = json.loads(response2.data)
    assert data["success"] is False
    assert "error" in data

def test_get_session_details_success(client, valid_session_data):
    """Testa a obtenção bem-sucedida dos detalhes de uma sessão."""
    # Primeiro inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Obtém os detalhes da sessão
    response = client.get(f"/api/v1/sessions/{session_id}")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["data"]["session_id"] == session_id
    assert data["data"]["station_id"] == valid_session_data["station_id"]
    assert data["data"]["wallet_address"] == valid_session_data["wallet_address"]
    assert data["data"]["status"] == SessionStatus.ACTIVE.value
    assert "start_time" in data["data"]

def test_get_session_details_not_found(client):
    """Testa a obtenção de detalhes de uma sessão inexistente."""
    session_id = 999
    response = client.get(f"/api/v1/sessions/{session_id}")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data 