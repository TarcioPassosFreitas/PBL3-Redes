from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type, Union, Tuple
import jwt
from flask import request, jsonify
from web3 import Web3
from functools import wraps

from domain.entities.session import Session
from domain.entities.station import Station
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    ResourceConflictError,
    BlockchainError,
    DatabaseError,
    CacheError,
    EmailError,
    PaymentError
)
from domain.ports.http_port import HTTPPort
from shared.constants.config import Config
from shared.constants.texts import Texts
from shared.utils.logger import Logger


class FlaskAdapter(HTTPPort):
    """
    Adaptador HTTP para Flask que implementa a interface HTTPPort.
    Responsável por adaptar requisições e respostas HTTP para o domínio da aplicação.
    """

    def __init__(self):
        self.logger = Logger(__name__)
        self.w3 = Web3()

    async def authenticate_request(self):
        """Valida o token JWT da requisição."""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                self.logger.error(Texts.ERROR_FLASK_AUTH)
                raise AuthenticationError(Texts.ERROR_FLASK_AUTH)
            
            token = auth_header.split(" ")[1]
            payload = self.jwt_adapter.validate_token(token)
            self.logger.info(Texts.format(Texts.LOG_FLASK_AUTH, "sucesso", payload["sub"]))
            return payload
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_FLASK_AUTH, str(e)))
            raise AuthenticationError(Texts.format(Texts.ERROR_FLASK_AUTH, str(e)))

    async def validate_request_body(
        self,
        body: Dict[str, Any] = None,
        required_fields: Dict[str, type] = None
    ) -> Dict[str, Any]:
        """
        Valida o corpo da requisição contra os campos obrigatórios.
        
        Args:
            required_fields: Dicionário com nome e tipo dos campos obrigatórios
            
        Returns:
            Dict[str, Any]: Dados validados da requisição
            
        Raises:
            ValidationError: Se algum campo obrigatório estiver ausente ou inválido
        """
        if body is None:
            body = request.get_json()
        if not body:
            raise ValidationError(Texts.ERROR_VALIDATION_MISSING_BODY)

        if required_fields:
            for field, field_type in required_fields.items():
                if field not in body:
                    raise ValidationError(
                        Texts.format(Texts.VALIDATION_MISSING_REQUIRED_FIELD, field)
                    )
                if not isinstance(body[field], field_type):
                    raise ValidationError(
                        Texts.format(Texts.VALIDATION_INVALID_FIELD_TYPE, field)
                    )

        return body

    async def create_response(
        self,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        status_code: int = 200
    ) -> Tuple[Dict[str, Any], int]:
        """
        Cria uma resposta HTTP padronizada.
        
        Args:
            data: Dados a serem retornados
            message: Mensagem associada à resposta
            status_code: Código de status HTTP
            
        Returns:
            tuple: Resposta HTTP (resposta, código)
        """
        try:
            self.logger.info(Texts.format(Texts.LOG_FLASK_RESPONSE, status_code, request.path))
            response = {
                "success": True,
                "message": message or Texts.SUCCESS,
                "data": data
            }
            return jsonify(response), status_code
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_FLASK_RESPONSE, status_code, request.path, str(e)))
            raise ValidationError(Texts.format(Texts.ERROR_FLASK_RESPONSE, status_code, request.path, str(e)))

    async def create_error_response(
        self,
        error: Exception,
        status_code: int = 400
    ) -> Tuple[Dict[str, Any], int]:
        """
        Create a standardized error response.
        """
        if hasattr(error, "code"):
            error_code = error.code
        else:
            error_code = "UNKNOWN_ERROR"

        if hasattr(error, "message"):
            error_message = error.message
        else:
            error_message = str(error)

        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
        return jsonify(response), status_code

    async def validate_wallet_address(self, wallet_address: str) -> bool:
        """
        Valida um endereço de carteira Ethereum.
        
        Args:
            address: Endereço da carteira a ser validado
            
        Returns:
            bool: True se o endereço for válido, False caso contrário
        """
        try:
            return self.w3.is_address(wallet_address)
        except Exception:
            return False

    async def validate_signature(
        self,
        message: str,
        signature: str,
        wallet_address: str
    ) -> bool:
        """
        Valida uma assinatura Ethereum.
        
        Args:
            message: Mensagem original
            signature: Assinatura a ser validada
            address: Endereço da carteira que assinou
            
        Returns:
            bool: True se a assinatura for válida, False caso contrário
        """
        try:
            message_hash = self.w3.keccak(text=message)
            recovered_address = self.w3.eth.account.recover_message(
                message_hash,
                signature=signature
            )
            return recovered_address.lower() == wallet_address.lower()
        except Exception:
            return False

    async def format_session_response(self, session: Session) -> Dict[str, Any]:
        """
        Format a session entity for HTTP response.
        """
        return {
            "id": session.id,
            "user_address": session.user_address,
            "station_id": session.station_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "is_active": session.is_active,
            "is_paid": session.is_paid,
            "amount": str(session.amount) if session.amount else None,
            "duration": session.duration,
            "duration_hours": session.duration_hours
        }

    async def format_station_response(self, station: Station) -> Dict[str, Any]:
        """
        Format a station entity for HTTP response.
        """
        return {
            "id": station.id,
            "location": station.location,
            "power_output": str(station.power_output),
            "is_available": station.is_available,
            "current_session_id": station.current_session_id,
            "price_per_hour": str(station.price_per_hour),
            "reservations": {
                dt.isoformat(): user
                for dt, user in station.reservations.items()
            }
        }

    async def format_user_response(self, user: User) -> Dict[str, Any]:
        """
        Format a user entity for HTTP response.
        """
        return {
            "wallet_address": user.wallet_address,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "active_sessions": user.active_sessions,
            "total_charges": str(user.total_charges),
            "total_sessions": user.total_sessions
        }

    async def parse_datetime(self, datetime_str: str) -> datetime:
        """
        Converte uma string de data/hora para objeto datetime.
        
        Args:
            date_str: String de data/hora no formato ISO 8601
            
        Returns:
            datetime: Objeto datetime
            
        Raises:
            ValidationError: Se a string estiver em formato inválido
        """
        try:
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValidationError(
                Texts.format(Texts.VALIDATION_INVALID_DATETIME, str(e))
            )

    async def parse_decimal(self, decimal_str: str) -> Decimal:
        """
        Converte uma string decimal para objeto Decimal.
        
        Args:
            decimal_str: String decimal
            
        Returns:
            Decimal: Objeto Decimal
            
        Raises:
            ValidationError: Se a string não for um decimal válido
        """
        try:
            return Decimal(decimal_str)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                Texts.format(Texts.VALIDATION_INVALID_AMOUNT, str(e))
            )

    def get_user_address(self) -> str:
        """Obtém o endereço do usuário autenticado."""
        try:
            payload = self.authenticate_request()
            return payload["sub"]
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_FLASK_AUTH, str(e)))
            raise AuthenticationError(Texts.format(Texts.ERROR_FLASK_AUTH, str(e)))

    def parse_date(self, date_str: str) -> datetime:
        """Converte uma string em data."""
        try:
            if not date_str:
                return None
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_FLASK_VALIDATION, f"Data inválida: {date_str}"))
            raise ValidationError(Texts.format(Texts.ERROR_FLASK_VALIDATION, f"Data inválida: {date_str}"))

    def handle_error(self, error):
        """Trata erros da aplicação."""
        try:
            if isinstance(error, AuthenticationError):
                self.logger.error(Texts.format(Texts.ERROR_FLASK_AUTH, str(error)))
                return jsonify({"error": str(error)}), 401
                
            elif isinstance(error, ValidationError):
                self.logger.error(Texts.format(Texts.ERROR_FLASK_VALIDATION, str(error)))
                return jsonify({"error": str(error)}), 400
                
            elif isinstance(error, ResourceNotFoundError):
                self.logger.error(Texts.format(Texts.ERROR_FLASK_REQUEST, "404", request.path, str(error)))
                return jsonify({"error": str(error)}), 404
                
            elif isinstance(error, (DatabaseError, CacheError, EmailError, PaymentError, BlockchainError)):
                self.logger.error(Texts.format(Texts.ERROR_FLASK_REQUEST, "500", request.path, str(error)))
                return jsonify({"error": str(error)}), 500
                
            else:
                self.logger.error(Texts.format(Texts.ERROR_FLASK_REQUEST, "500", request.path, str(error)))
                return jsonify({"error": "Erro interno do servidor"}), 500
                
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_FLASK_RESPONSE, "500", request.path, str(e)))
            return jsonify({"error": "Erro interno do servidor"}), 500

    def validate_request_body(self, required_fields: Dict[str, Type]) -> Dict[str, Any]:
        """
        Valida o corpo da requisição contra os campos obrigatórios.
        
        Args:
            required_fields: Dicionário com nome e tipo dos campos obrigatórios
            
        Returns:
            Dict[str, Any]: Dados validados da requisição
            
        Raises:
            ValidationError: Se algum campo obrigatório estiver ausente ou inválido
        """
        try:
            # Obtém dados da requisição
            data = self.request.get_json()
            if not data:
                raise ValidationError(Texts.ERROR_VALIDATION_MISSING_BODY)
                
            # Valida campos obrigatórios
            for field, field_type in required_fields.items():
                if field not in data:
                    raise ValidationError(Texts.format(Texts.VALIDATION_MISSING_REQUIRED_FIELD, field))
                if not isinstance(data[field], field_type):
                    raise ValidationError(Texts.format(Texts.VALIDATION_INVALID_FIELD_TYPE, field))
                    
            return data
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_VALIDATION_REQUEST, str(e)))
            raise ValidationError(Texts.VALIDATION_ERROR)

    def create_response(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        status_code: int = 200
    ) -> tuple:
        """
        Cria uma resposta HTTP padronizada.
        
        Args:
            data: Dados a serem retornados
            status_code: Código de status HTTP
            
        Returns:
            tuple: Resposta HTTP (resposta, código)
        """
        response = {
            "success": True,
            "data": data
        }
        return jsonify(response), status_code
        
    def parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Converte uma string de data/hora para objeto datetime.
        
        Args:
            date_str: String de data/hora no formato ISO 8601
            
        Returns:
            Optional[datetime]: Objeto datetime ou None se a string for None
            
        Raises:
            ValidationError: Se a string estiver em formato inválido
        """
        if not date_str:
            return None
            
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValidationError(Texts.format(Texts.VALIDATION_INVALID_DATETIME, str(e)))
            
    def parse_decimal(self, decimal_str: Optional[str]) -> Optional[Decimal]:
        """
        Converte uma string decimal para objeto Decimal.
        
        Args:
            decimal_str: String decimal
            
        Returns:
            Optional[Decimal]: Objeto Decimal ou None se a string for None
            
        Raises:
            ValidationError: Se a string não for um decimal válido
        """
        if not decimal_str:
            return None
            
        try:
            return Decimal(decimal_str)
        except (ValueError, TypeError) as e:
            raise ValidationError(Texts.format(Texts.VALIDATION_INVALID_AMOUNT, str(e)))
            
    def validate_wallet_address(self, address: str) -> bool:
        """
        Valida um endereço de carteira Ethereum.
        
        Args:
            address: Endereço da carteira a ser validado
            
        Returns:
            bool: True se o endereço for válido, False caso contrário
        """
        if not address or not isinstance(address, str):
            return False
            
        # Remove prefixo 0x se presente
        address = address.lower().replace("0x", "")
        
        # Verifica comprimento e caracteres válidos
        if len(address) != 40 or not all(c in "0123456789abcdef" for c in address):
            return False
            
        return True
        
    def validate_signature(self, message: str, signature: str, address: str) -> bool:
        """
        Valida uma assinatura Ethereum.
        
        Args:
            message: Mensagem original
            signature: Assinatura a ser validada
            address: Endereço da carteira que assinou
            
        Returns:
            bool: True se a assinatura for válida, False caso contrário
        """
        # TODO: Implementar validação de assinatura usando web3.py
        return True

    async def format_error_response(self, error, status_code=400):
        return {
            "success": False,
            "error": {
                "code": getattr(error, 'code', 'UNKNOWN_ERROR'),
                "message": str(error)
            }
        }, status_code

    async def format_reservation_response(self, reservation):
        return {
            "id": getattr(reservation, 'id', None),
            "user": getattr(reservation, 'user', None),
            "start_time": getattr(reservation, 'start_time', None),
            "end_time": getattr(reservation, 'end_time', None),
            "active": getattr(reservation, 'active', None)
        } 