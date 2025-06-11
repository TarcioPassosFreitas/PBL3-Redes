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
    return "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1b"

@pytest.fixture
def valid_session_data(valid_wallet_address, valid_signature):
    """Fixture que retorna dados válidos para uma sessão."""
    return {
        "station_id": 1,
        "wallet_address": valid_wallet_address,
        "signature": valid_signature
    }

@pytest.fixture
def valid_payment_data(valid_wallet_address, valid_signature):
    """Fixture que retorna dados válidos para um pagamento."""
    return {
        "session_id": 1,
        "wallet_address": valid_wallet_address,
        "signature": valid_signature
    }

def test_process_payment_success(client, valid_session_data, valid_payment_data):
    """Testa o processamento bem-sucedido de um pagamento via API."""
    # Primeiro inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Finaliza a sessão
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200
    
    # Processa o pagamento
    payment_data = {
        "wallet_address": valid_payment_data["wallet_address"],
        "signature": valid_payment_data["signature"]
    }
    response = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(payment_data),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["data"]["session_id"] == session_id
    assert data["data"]["status"] == SessionStatus.PAID.value
    assert "payment_amount" in data["data"]
    assert "payment_time" in data["data"]

def test_process_payment_invalid_data(client):
    """Testa o processamento de pagamento com dados inválidos."""
    session_id = 1
    invalid_data = {
        "wallet_address": "invalid",
        "signature": "invalid"
    }
    
    response = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(invalid_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_process_payment_missing_data(client):
    """Testa o processamento de pagamento com dados faltando."""
    session_id = 1
    incomplete_data = {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }
    
    response = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(incomplete_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_process_payment_session_not_found(client, valid_payment_data):
    """Testa o processamento de pagamento para sessão inexistente."""
    session_id = 999
    payment_data = {
        "wallet_address": valid_payment_data["wallet_address"],
        "signature": valid_payment_data["signature"]
    }
    
    response = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(payment_data),
        content_type="application/json"
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_process_payment_session_not_ended(client, valid_session_data, valid_payment_data):
    """Testa o processamento de pagamento para sessão não finalizada."""
    # Inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Tenta processar pagamento sem finalizar a sessão
    payment_data = {
        "wallet_address": valid_payment_data["wallet_address"],
        "signature": valid_payment_data["signature"]
    }
    response = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(payment_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_process_payment_already_paid(client, valid_session_data, valid_payment_data):
    """Testa o processamento de pagamento para sessão já paga."""
    # Inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Finaliza a sessão
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200
    
    # Processa o primeiro pagamento
    payment_data = {
        "wallet_address": valid_payment_data["wallet_address"],
        "signature": valid_payment_data["signature"]
    }
    response1 = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(payment_data),
        content_type="application/json"
    )
    assert response1.status_code == 200
    
    # Tenta processar o pagamento novamente
    response2 = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(payment_data),
        content_type="application/json"
    )
    
    assert response2.status_code == 409
    data = json.loads(response2.data)
    assert data["success"] is False
    assert "error" in data

def test_get_payment_history_success(client, valid_wallet_address):
    """Testa a obtenção bem-sucedida do histórico de pagamentos via API."""
    response = client.get(f"/api/v1/users/{valid_wallet_address}/payments")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all(isinstance(payment, dict) for payment in data)
    assert all("session_id" in payment for payment in data)
    assert all("payment_amount" in payment for payment in data)
    assert all("payment_time" in payment for payment in data)

def test_get_payment_history_not_found(client):
    """Testa a obtenção de histórico de pagamentos para usuário inexistente."""
    invalid_wallet = "0x0000000000000000000000000000000000000000"
    response = client.get(f"/api/v1/users/{invalid_wallet}/payments")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_get_session_payment_details_success(client, valid_session_data, valid_payment_data):
    """Testa a obtenção bem-sucedida dos detalhes do pagamento de uma sessão."""
    # Inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Finaliza a sessão
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200
    
    # Processa o pagamento
    payment_data = {
        "wallet_address": valid_payment_data["wallet_address"],
        "signature": valid_payment_data["signature"]
    }
    payment_response = client.post(
        f"/api/v1/sessions/{session_id}/payment",
        data=json.dumps(payment_data),
        content_type="application/json"
    )
    assert payment_response.status_code == 200
    
    # Obtém os detalhes do pagamento
    response = client.get(f"/api/v1/sessions/{session_id}/payment")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["data"]["session_id"] == session_id
    assert "payment_amount" in data["data"]
    assert "payment_time" in data["data"]
    assert "status" in data["data"]

def test_get_session_payment_details_not_found(client):
    """Testa a obtenção de detalhes de pagamento para sessão inexistente."""
    session_id = 999
    response = client.get(f"/api/v1/sessions/{session_id}/payment")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_get_session_payment_details_not_paid(client, valid_session_data):
    """Testa a obtenção de detalhes de pagamento para sessão não paga."""
    # Inicia uma sessão
    start_response = client.post(
        "/api/v1/sessions",
        data=json.dumps(valid_session_data),
        content_type="application/json"
    )
    assert start_response.status_code == 201
    session_id = json.loads(start_response.data)["data"]["session_id"]
    
    # Finaliza a sessão
    end_response = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_response.status_code == 200
    
    # Tenta obter detalhes do pagamento
    response = client.get(f"/api/v1/sessions/{session_id}/payment")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data 