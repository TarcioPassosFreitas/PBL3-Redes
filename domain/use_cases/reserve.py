from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

from domain.entities.station import Station
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    StationNotFoundError,
    UserNotFoundError,
    ValidationError,
    StationInUseError,
    StationAlreadyReservedError,
    ReservationNotFoundError,
    ReservationExpiredError
)
from domain.ports.blockchain_port import BlockchainPort
from domain.ports.http_port import HTTPPort
from domain.ports.database_port import DatabasePort
from domain.ports.notification_port import NotificationPort
from shared.utils.logger import Logger
from shared.constants.texts import Texts


class ReserveUseCase:
    """
    Caso de uso para gerenciamento de reservas de estações.
    Esta classe implementa a lógica de negócio para reservar e cancelar reservas.
    """

    def __init__(self, blockchain_port: BlockchainPort, http_port: HTTPPort):
        self.blockchain_port = blockchain_port
        self.http_port = http_port

    async def reserve_station(
        self,
        user_address: str,
        station_id: int,
        start_time_str: str,
        duration_hours_str: str
    ) -> dict:
        """
        Reserva uma estação de carregamento para um horário específico.
        
        Args:
            user_address: O endereço da carteira do usuário
            station_id: O ID da estação a ser reservada
            start_time_str: O horário de início da reserva (ISO format)
            duration_hours_str: A duração da reserva em horas
            
        Returns:
            Um dicionário com os detalhes da reserva
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            StationNotFoundError: Se a estação não existir
            StationInUseError: Se a estação estiver em uso
            StationAlreadyReservedError: Se a estação já estiver reservada
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Converte e valida horário de início
        try:
            start_time = await self.http_port.parse_datetime(start_time_str)
        except ValueError as e:
            raise ValidationError(Texts.format(Texts.VALIDATION_INVALID_DATETIME, str(e)))

        # Converte e valida duração
        try:
            duration_hours = float(duration_hours_str)
        except ValueError:
            raise ValidationError(Texts.VALIDATION_INVALID_DURATION)

        # Valida duração mínima e máxima
        if duration_hours < 1:
            raise ValidationError(Texts.STATION_RESERVATION_TOO_SHORT)
        if duration_hours > 24:
            raise ValidationError(Texts.STATION_RESERVATION_TOO_LONG)

        # Valida horário de início (não pode ser no passado)
        if start_time < datetime.utcnow():
            raise ValidationError(Texts.VALIDATION_INVALID_START_TIME)

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

        # Verifica se estação já está reservada no período
        end_time = start_time + timedelta(hours=duration_hours)
        if await self.blockchain_port.is_station_reserved_in_period(station_id, start_time, end_time):
            raise StationAlreadyReservedError(station_id)

        # Cria reserva na blockchain
        reservation_id = await self.blockchain_port.reserve_station(
            user_address=user_address,
            station_id=station_id,
            start_time=start_time,
            duration_hours=duration_hours
        )

        # Obtém detalhes da reserva
        reservation = await self.blockchain_port.get_reservation(reservation_id)

        # Retorna detalhes da reserva
        return {
            "reservation_id": reservation_id,
            "user_address": user_address,
            "station_id": station_id,
            "start_time": reservation.start_time.isoformat(),
            "end_time": reservation.end_time.isoformat(),
            "duration_hours": reservation.duration_hours,
            "status": "active",
            "reservation": await self.http_port.format_reservation_response(reservation)
        }

    async def cancel_reservation(
        self,
        user_address: str,
        reservation_id: int
    ) -> dict:
        """
        Cancela uma reserva de estação.
        
        Args:
            user_address: O endereço da carteira do usuário
            reservation_id: O ID da reserva a ser cancelada
            
        Returns:
            Um dicionário com os detalhes da reserva cancelada
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            ReservationNotFoundError: Se a reserva não existir
            ReservationExpiredError: Se a reserva já expirou
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Obtém usuário e reserva
        try:
            user = await self.blockchain_port.get_user(user_address)
            reservation = await self.blockchain_port.get_reservation(reservation_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except ReservationNotFoundError:
            raise ReservationNotFoundError(reservation_id)

        # Valida propriedade da reserva
        if reservation.user_address != user_address:
            raise ValidationError(Texts.RESERVATION_NOT_OWNED)

        # Verifica se reserva já expirou
        if reservation.end_time < datetime.utcnow():
            raise ReservationExpiredError(reservation_id)

        # Cancela reserva na blockchain
        await self.blockchain_port.cancel_reservation(reservation_id)

        # Obtém detalhes atualizados da reserva
        reservation = await self.blockchain_port.get_reservation(reservation_id)

        # Retorna detalhes da reserva
        return {
            "reservation_id": reservation_id,
            "user_address": user_address,
            "station_id": reservation.station_id,
            "start_time": reservation.start_time.isoformat(),
            "end_time": reservation.end_time.isoformat(),
            "duration_hours": reservation.duration_hours,
            "status": "cancelled",
            "reservation": await self.http_port.format_reservation_response(reservation)
        }

    async def get_reservation_details(
        self,
        user_address: str,
        reservation_id: int
    ) -> dict:
        """
        Obtém detalhes de uma reserva.
        
        Args:
            user_address: O endereço da carteira do usuário
            reservation_id: O ID da reserva para obter detalhes
            
        Returns:
            Um dicionário com os detalhes da reserva
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            ReservationNotFoundError: Se a reserva não existir
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Obtém usuário e reserva
        try:
            user = await self.blockchain_port.get_user(user_address)
            reservation = await self.blockchain_port.get_reservation(reservation_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except ReservationNotFoundError:
            raise ReservationNotFoundError(reservation_id)

        # Valida propriedade da reserva
        if reservation.user_address != user_address:
            raise ValidationError(Texts.RESERVATION_NOT_OWNED)

        # Determina status da reserva
        current_time = datetime.utcnow()
        if reservation.is_cancelled:
            status = "cancelled"
        elif current_time > reservation.end_time:
            status = "expired"
        elif current_time >= reservation.start_time:
            status = "active"
        else:
            status = "pending"

        # Retorna detalhes da reserva
        return {
            "reservation_id": reservation_id,
            "user_address": user_address,
            "station_id": reservation.station_id,
            "start_time": reservation.start_time.isoformat(),
            "end_time": reservation.end_time.isoformat(),
            "duration_hours": reservation.duration_hours,
            "status": status,
            "reservation": await self.http_port.format_reservation_response(reservation)
        }

    async def get_user_reservations(
        self,
        user_address: str,
        status: Optional[str] = None
    ) -> List[dict]:
        """
        Obtém todas as reservas de um usuário.
        
        Args:
            user_address: O endereço da carteira do usuário
            status: Filtro opcional por status (active, pending, expired, cancelled)
            
        Returns:
            Uma lista de dicionários com os detalhes das reservas
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Valida status se fornecido
        if status and status not in ["active", "pending", "expired", "cancelled"]:
            raise ValidationError(Texts.VALIDATION_INVALID_STATUS)

        # Obtém usuário
        try:
            user = await self.blockchain_port.get_user(user_address)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)

        # Obtém reservas do usuário
        reservations = await self.blockchain_port.get_user_reservations(user_address)

        # Filtra por status se necessário
        if status:
            current_time = datetime.utcnow()
            filtered_reservations = []
            for reservation in reservations:
                if reservation.is_cancelled and status == "cancelled":
                    filtered_reservations.append(reservation)
                elif current_time > reservation.end_time and status == "expired":
                    filtered_reservations.append(reservation)
                elif current_time >= reservation.start_time and status == "active":
                    filtered_reservations.append(reservation)
                elif current_time < reservation.start_time and status == "pending":
                    filtered_reservations.append(reservation)
            reservations = filtered_reservations

        # Formata e retorna reservas
        return [
            {
                "reservation_id": reservation.id,
                "user_address": user_address,
                "station_id": reservation.station_id,
                "start_time": reservation.start_time.isoformat(),
                "end_time": reservation.end_time.isoformat(),
                "duration_hours": reservation.duration_hours,
                "status": "cancelled" if reservation.is_cancelled else
                         "expired" if current_time > reservation.end_time else
                         "active" if current_time >= reservation.start_time else
                         "pending",
                "reservation": await self.http_port.format_reservation_response(reservation)
            }
            for reservation in reservations
        ] 