import pytest
from datetime import datetime, timedelta
import json

from app import create_app

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
def valid_reservation_data(valid_wallet_address, valid_signature):
    """Fixture que retorna dados válidos para uma reserva."""
    start_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    end_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    return {
        "station_id": 1,
        "wallet_address": valid_wallet_address,
        "start_time": start_time,
        "end_time": end_time,
        "signature": valid_signature
    }

def test_create_reservation_success(client, valid_reservation_data):
    """Testa a criação bem-sucedida de uma reserva via API."""
    response = client.post(
        "/api/v1/reservations",
        data=json.dumps(valid_reservation_data),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert "reservation_id" in data["data"]
    assert data["data"]["station_id"] == valid_reservation_data["station_id"]
    assert data["data"]["wallet_address"] == valid_reservation_data["wallet_address"]
    assert data["data"]["start_time"] == valid_reservation_data["start_time"]
    assert data["data"]["end_time"] == valid_reservation_data["end_time"]

def test_create_reservation_invalid_data(client):
    """Testa a criação de reserva com dados inválidos."""
    invalid_data = {
        "station_id": "invalid",
        "wallet_address": "invalid",
        "start_time": "invalid",
        "end_time": "invalid",
        "signature": "invalid"
    }
    
    response = client.post(
        "/api/v1/reservations",
        data=json.dumps(invalid_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_create_reservation_missing_data(client):
    """Testa a criação de reserva com dados faltando."""
    incomplete_data = {
        "station_id": 1,
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    }
    
    response = client.post(
        "/api/v1/reservations",
        data=json.dumps(incomplete_data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_cancel_reservation_success(client, valid_wallet_address, valid_signature):
    """Testa o cancelamento bem-sucedido de uma reserva via API."""
    reservation_id = 1
    data = {
        "wallet_address": valid_wallet_address,
        "signature": valid_signature
    }
    
    response = client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["data"]["reservation_id"] == reservation_id
    assert data["data"]["status"] == "cancelled"

def test_cancel_reservation_not_found(client, valid_wallet_address, valid_signature):
    """Testa o cancelamento de uma reserva inexistente."""
    reservation_id = 999
    data = {
        "wallet_address": valid_wallet_address,
        "signature": valid_signature
    }
    
    response = client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_get_user_reservations_success(client, valid_wallet_address):
    """Testa a obtenção bem-sucedida das reservas de um usuário via API."""
    response = client.get(f"/api/v1/users/{valid_wallet_address}/reservations")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all(isinstance(reservation, dict) for reservation in data)
    assert all("reservation_id" in reservation for reservation in data)
    assert all("station_id" in reservation for reservation in data)
    assert all("start_time" in reservation for reservation in data)
    assert all("end_time" in reservation for reservation in data)

def test_get_user_reservations_not_found(client):
    """Testa a obtenção de reservas de um usuário inexistente."""
    invalid_wallet = "0x0000000000000000000000000000000000000000"
    response = client.get(f"/api/v1/users/{invalid_wallet}/reservations")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_get_station_reservations_success(client):
    """Testa a obtenção bem-sucedida das reservas de uma estação via API."""
    station_id = 1
    response = client.get(f"/api/v1/stations/{station_id}/reservations")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert all(isinstance(reservation, dict) for reservation in data)
    assert all("reservation_id" in reservation for reservation in data)
    assert all("wallet_address" in reservation for reservation in data)
    assert all("start_time" in reservation for reservation in data)
    assert all("end_time" in reservation for reservation in data)

def test_get_station_reservations_not_found(client):
    """Testa a obtenção de reservas de uma estação inexistente."""
    station_id = 999
    response = client.get(f"/api/v1/stations/{station_id}/reservations")
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_create_reservation_time_overlap(client, valid_reservation_data):
    """Testa a criação de reserva com sobreposição de horário."""
    # Criar primeira reserva
    response1 = client.post(
        "/api/v1/reservations",
        data=json.dumps(valid_reservation_data),
        content_type="application/json"
    )
    assert response1.status_code == 201
    
    # Tentar criar segunda reserva com mesmo horário
    response2 = client.post(
        "/api/v1/reservations",
        data=json.dumps(valid_reservation_data),
        content_type="application/json"
    )
    
    assert response2.status_code == 409
    data = json.loads(response2.data)
    assert data["success"] is False
    assert "error" in data

def test_create_reservation_past_time(client, valid_wallet_address, valid_signature):
    """Testa a criação de reserva com horário no passado."""
    past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    data = {
        "station_id": 1,
        "wallet_address": valid_wallet_address,
        "start_time": past_time,
        "end_time": future_time,
        "signature": valid_signature
    }
    
    response = client.post(
        "/api/v1/reservations",
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data

def test_create_reservation_invalid_time_range(client, valid_wallet_address, valid_signature):
    """Testa a criação de reserva com horário de fim anterior ao início."""
    start_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    end_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    data = {
        "station_id": 1,
        "wallet_address": valid_wallet_address,
        "start_time": start_time,
        "end_time": end_time,
        "signature": valid_signature
    }
    
    response = client.post(
        "/api/v1/reservations",
        data=json.dumps(data),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    assert "error" in data 