from datetime import datetime
from decimal import Decimal
from typing import Optional

from domain.entities.session import Session
from domain.entities.station import Station
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    SessionNotFoundError,
    StationNotFoundError,
    UserNotFoundError,
    ValidationError,
    StationInUseError,
    StationNotReservedError,
    SessionAlreadyActiveError,
    SessionNotActiveError
)
from domain.ports.blockchain_port import BlockchainPort
from domain.ports.http_port import HTTPPort
from domain.ports.database_port import DatabasePort
from domain.ports.notification_port import NotificationPort
from shared.utils.logger import Logger
from shared.constants.texts import Texts


class ChargeUseCase:
    """
    Caso de uso para gerenciamento de sessões de carregamento.
    Esta classe implementa a lógica de negócio para iniciar e finalizar sessões.
    """

    def __init__(self, blockchain_port: BlockchainPort, http_port: HTTPPort):
        self.blockchain_port = blockchain_port
        self.http_port = http_port

    async def start_session(
        self,
        user_address: str,
        station_id: int
    ) -> dict:
        """
        Inicia uma nova sessão de carregamento.
        
        Args:
            user_address: O endereço da carteira do usuário
            station_id: O ID da estação de carregamento
            
        Returns:
            Um dicionário com os detalhes da sessão iniciada
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            StationNotFoundError: Se a estação não existir
            StationInUseError: Se a estação estiver em uso
            StationNotReservedError: Se a estação não estiver reservada para o usuário
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Obtém usuário e estação
        try:
            user = await self.blockchain_port.get_user(user_address)
            station = await self.blockchain_port.get_station(station_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except StationNotFoundError:
            raise StationNotFoundError(station_id)

        # Verifica se estação está disponível
        if not station.is_available:
            raise StationInUseError(station_id)

        # Verifica se estação está reservada para o usuário
        if not await self.blockchain_port.is_station_reserved_for_user(station_id, user_address):
            raise StationNotReservedError(station_id)

        # Inicia sessão na blockchain
        session_id = await self.blockchain_port.start_session(
            user_address=user_address,
            station_id=station_id
        )

        # Obtém detalhes da sessão iniciada
        session = await self.blockchain_port.get_session(session_id)

        # Retorna detalhes da sessão
        return {
            "session_id": session_id,
            "user_address": user_address,
            "station_id": station_id,
            "start_time": session.start_time.isoformat(),
            "status": "active",
            "session": await self.http_port.format_session_response(session)
        }

    async def end_session(
        self,
        user_address: str,
        session_id: int
    ) -> dict:
        """
        Finaliza uma sessão de carregamento ativa.
        
        Args:
            user_address: O endereço da carteira do usuário
            session_id: O ID da sessão a ser finalizada
            
        Returns:
            Um dicionário com os detalhes da sessão finalizada
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            SessionNotFoundError: Se a sessão não existir
            SessionNotActiveError: Se a sessão não estiver ativa
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Obtém usuário e sessão
        try:
            user = await self.blockchain_port.get_user(user_address)
            session = await self.blockchain_port.get_session(session_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except SessionNotFoundError:
            raise SessionNotFoundError(session_id)

        # Valida propriedade da sessão
        if session.user_address != user_address:
            raise ValidationError(Texts.SESSION_NOT_OWNED)

        # Verifica se sessão está ativa
        if not session.is_active:
            raise SessionNotActiveError(session_id)

        # Finaliza sessão na blockchain
        await self.blockchain_port.end_session(session_id)

        # Obtém detalhes atualizados da sessão
        session = await self.blockchain_port.get_session(session_id)

        # Calcula valor do pagamento
        required_amount = self._calculate_payment_amount(session)

        # Retorna detalhes da sessão
        return {
            "session_id": session_id,
            "user_address": user_address,
            "station_id": session.station_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat(),
            "duration_hours": session.duration_hours,
            "required_payment": str(required_amount),
            "status": "ended",
            "session": await self.http_port.format_session_response(session)
        }

    async def get_session_details(
        self,
        user_address: str,
        session_id: int
    ) -> dict:
        """
        Obtém detalhes de uma sessão de carregamento.
        
        Args:
            user_address: O endereço da carteira do usuário
            session_id: O ID da sessão para obter detalhes
            
        Returns:
            Um dicionário com os detalhes da sessão
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            SessionNotFoundError: Se a sessão não existir
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Obtém usuário e sessão
        try:
            user = await self.blockchain_port.get_user(user_address)
            session = await self.blockchain_port.get_session(session_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except SessionNotFoundError:
            raise SessionNotFoundError(session_id)

        # Valida propriedade da sessão
        if session.user_address != user_address:
            raise ValidationError(Texts.SESSION_NOT_OWNED)

        # Calcula valor do pagamento se sessão estiver finalizada mas não paga
        required_amount = None
        if not session.is_active and not session.is_paid:
            required_amount = str(self._calculate_payment_amount(session))

        # Retorna detalhes da sessão
        return {
            "session_id": session_id,
            "user_address": user_address,
            "station_id": session.station_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_hours": session.duration_hours,
            "required_payment": required_amount,
            "status": "active" if session.is_active else "ended" if session.end_time else "paid" if session.is_paid else "unknown",
            "session": await self.http_port.format_session_response(session)
        }

    def _calculate_payment_amount(self, session: Session) -> float:
        """
        Calcula o valor do pagamento necessário para uma sessão.
        
        Args:
            session: A sessão para calcular o pagamento
            
        Returns:
            O valor do pagamento necessário em ETH
        """
        if not session.duration:
            raise ValidationError(Texts.VALIDATION_ACTIVE_SESSION_PAYMENT)

        # Taxa base: 0.001 ETH por hora
        base_rate = 0.001
        
        # Calcula horas (arredonda para cima para hora mais próxima)
        hours = session.duration_hours
        if hours % 1 != 0:
            hours = int(hours) + 1
        
        return base_rate * hours

    async def get_user_sessions(
        self,
        user_address: str,
        active_only: bool = False
    ) -> list[dict]:
        """
        Get all sessions for a user.
        
        Args:
            user_address: The wallet address of the user
            active_only: Whether to return only active sessions
            
        Returns:
            A list of dictionaries with session details
            
        Raises:
            ValidationError: If the input data is invalid
            UserNotFoundError: If the user doesn't exist
        """
        # Validate wallet address
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Get user
        try:
            user = await self.blockchain_port.get_user(user_address)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)

        # Get all sessions for user
        sessions = []
        for session_id in user.active_sessions if active_only else range(1, user.total_sessions + 1):
            try:
                session = await self.blockchain_port.get_session(session_id)
                if session.user_address == user_address:
                    sessions.append(await self.http_port.format_session_response(session))
            except SessionNotFoundError:
                continue

        return sessions 