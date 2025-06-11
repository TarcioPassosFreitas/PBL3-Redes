from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type, Union

from domain.entities.session import Session
from domain.entities.station import Station
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    ValidationError,
    ResourceNotFoundError,
    ResourceConflictError,
    BlockchainError
)


class HTTPPort(ABC):
    """
    Interface para adaptadores HTTP.
    Define os métodos necessários para interação com requisições HTTP.
    """

    @abstractmethod
    async def validate_wallet_address(self, address: str) -> bool:
        """
        Valida um endereço de carteira Ethereum.
        
        Args:
            address: O endereço da carteira a ser validado
            
        Returns:
            True se o endereço for válido, False caso contrário
        """
        pass

    @abstractmethod
    async def validate_signature(self, message: str, signature: str, address: str) -> bool:
        """
        Valida uma assinatura Ethereum.
        
        Args:
            message: A mensagem que foi assinada
            signature: A assinatura a ser validada
            address: O endereço da carteira que assinou
            
        Returns:
            True se a assinatura for válida, False caso contrário
        """
        pass

    @abstractmethod
    async def parse_datetime(self, datetime_str: str) -> datetime:
        """
        Converte uma string em um objeto datetime.
        
        Args:
            datetime_str: A string de data/hora no formato ISO
            
        Returns:
            O objeto datetime correspondente
            
        Raises:
            ValidationError: Se a string não estiver em um formato válido
        """
        pass

    @abstractmethod
    async def parse_date(self, date_str: str) -> datetime:
        """
        Converte uma string em um objeto date.
        
        Args:
            date_str: A string de data no formato ISO
            
        Returns:
            O objeto date correspondente
            
        Raises:
            ValidationError: Se a string não estiver em um formato válido
        """
        pass

    @abstractmethod
    async def parse_decimal(self, decimal_str: str) -> Decimal:
        """
        Converte uma string em um objeto Decimal.
        
        Args:
            decimal_str: A string decimal a ser convertida
            
        Returns:
            O objeto Decimal correspondente
            
        Raises:
            ValidationError: Se a string não representar um número decimal válido
        """
        pass

    @abstractmethod
    async def validate_request_body(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        field_types: Optional[Dict[str, Type]] = None
    ) -> None:
        """
        Valida o corpo da requisição contra os campos obrigatórios.
        
        Args:
            data: O dicionário com os dados da requisição
            required_fields: Lista de campos obrigatórios
            field_types: Dicionário opcional mapeando campos para seus tipos esperados
            
        Raises:
            ValidationError: Se algum campo obrigatório estiver faltando ou tiver tipo inválido
        """
        pass

    @abstractmethod
    async def create_response(
        self,
        data: Any = None,
        message: Optional[str] = None,
        status_code: int = 200
    ) -> Dict[str, Any]:
        """
        Cria uma resposta HTTP padronizada.
        
        Args:
            data: Os dados a serem retornados na resposta
            message: Uma mensagem opcional para a resposta
            status_code: O código de status HTTP da resposta
            
        Returns:
            Um dicionário com a resposta formatada
        """
        pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Trata erros e retorna respostas HTTP apropriadas.
        
        Args:
            error: A exceção a ser tratada
            
        Returns:
            Um dicionário com a resposta de erro formatada
        """
        pass

    @abstractmethod
    async def format_user_response(self, user: User) -> Dict[str, Any]:
        """
        Formata os dados do usuário para resposta HTTP.
        
        Args:
            user: O objeto User a ser formatado
            
        Returns:
            Um dicionário com os dados do usuário formatados
        """
        pass

    @abstractmethod
    async def format_station_response(self, station: Station) -> Dict[str, Any]:
        """
        Formata os dados da estação para resposta HTTP.
        
        Args:
            station: O objeto Station a ser formatado
            
        Returns:
            Um dicionário com os dados da estação formatados
        """
        pass

    @abstractmethod
    async def format_session_response(self, session: Session) -> Dict[str, Any]:
        """
        Formata os dados da sessão para resposta HTTP.
        
        Args:
            session: O objeto Session a ser formatado
            
        Returns:
            Um dicionário com os dados da sessão formatados
        """
        pass

    @abstractmethod
    async def format_reservation_response(self, reservation: Any) -> Dict[str, Any]:
        """
        Formata os dados da reserva para resposta HTTP.
        
        Args:
            reservation: O objeto Reservation a ser formatado
            
        Returns:
            Um dicionário com os dados da reserva formatados
        """
        pass

    @abstractmethod
    async def format_error_response(
        self,
        error: Union[ValidationError, ResourceNotFoundError, ResourceConflictError, BlockchainError],
        status_code: int
    ) -> Dict[str, Any]:
        """
        Formata uma resposta de erro HTTP.
        
        Args:
            error: A exceção de erro a ser formatada
            status_code: O código de status HTTP da resposta
            
        Returns:
            Um dicionário com a resposta de erro formatada
        """
        pass

    @abstractmethod
    async def get_user_address(self) -> str:
        """
        Obtém o endereço da carteira do usuário autenticado.
        
        Returns:
            O endereço da carteira do usuário
            
        Raises:
            ValidationError: Se não houver usuário autenticado
        """
        pass

    @abstractmethod
    async def authenticate_request(self) -> None:
        """
        Autentica a requisição atual usando o token JWT.
        
        Raises:
            ValidationError: Se o token for inválido ou expirado
        """
        pass 