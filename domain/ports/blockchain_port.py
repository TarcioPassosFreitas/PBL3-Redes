from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from domain.entities.session import Session
from domain.entities.station import Station
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    BlockchainError,
    ResourceNotFoundError,
    ResourceConflictError,
    ValidationError
)


class BlockchainPort(ABC):
    """
    Interface para adaptadores de blockchain.
    Define os métodos necessários para interação com a blockchain Ethereum.
    """

    @abstractmethod
    async def get_user(self, address: str) -> User:
        """
        Obtém os dados de um usuário da blockchain.
        
        Args:
            address: O endereço da carteira do usuário
            
        Returns:
            O objeto User com os dados do usuário
            
        Raises:
            ResourceNotFoundError: Se o usuário não existir
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_station(self, station_id: int) -> Station:
        """
        Obtém os dados de uma estação da blockchain.
        
        Args:
            station_id: O ID da estação
            
        Returns:
            O objeto Station com os dados da estação
            
        Raises:
            ResourceNotFoundError: Se a estação não existir
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: int) -> Session:
        """
        Obtém os dados de uma sessão da blockchain.
        
        Args:
            session_id: O ID da sessão
            
        Returns:
            O objeto Session com os dados da sessão
            
        Raises:
            ResourceNotFoundError: Se a sessão não existir
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_reservation(self, reservation_id: int) -> Any:
        """
        Obtém os dados de uma reserva da blockchain.
        
        Args:
            reservation_id: O ID da reserva
            
        Returns:
            O objeto Reservation com os dados da reserva
            
        Raises:
            ResourceNotFoundError: Se a reserva não existir
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_user_sessions(
        self,
        user_address: str,
        status: Optional[str] = None
    ) -> List[Session]:
        """
        Obtém todas as sessões de um usuário.
        
        Args:
            user_address: O endereço da carteira do usuário
            status: Filtro opcional por status (active, ended, paid)
            
        Returns:
            Lista de objetos Session com as sessões do usuário
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_user_reservations(
        self,
        user_address: str,
        status: Optional[str] = None
    ) -> List[Any]:
        """
        Obtém todas as reservas de um usuário.
        
        Args:
            user_address: O endereço da carteira do usuário
            status: Filtro opcional por status (active, pending, expired, cancelled)
            
        Returns:
            Lista de objetos Reservation com as reservas do usuário
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_station_sessions(
        self,
        station_id: int,
        status: Optional[str] = None
    ) -> List[Session]:
        """
        Obtém todas as sessões de uma estação.
        
        Args:
            station_id: O ID da estação
            status: Filtro opcional por status (active, ended, paid)
            
        Returns:
            Lista de objetos Session com as sessões da estação
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_station_reservations(
        self,
        station_id: int,
        status: Optional[str] = None
    ) -> List[Any]:
        """
        Obtém todas as reservas de uma estação.
        
        Args:
            station_id: O ID da estação
            status: Filtro opcional por status (active, pending, expired, cancelled)
            
        Returns:
            Lista de objetos Reservation com as reservas da estação
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def start_session(
        self,
        user_address: str,
        station_id: int
    ) -> int:
        """
        Inicia uma nova sessão de carregamento.
        
        Args:
            user_address: O endereço da carteira do usuário
            station_id: O ID da estação
            
        Returns:
            O ID da sessão criada
            
        Raises:
            ResourceConflictError: Se a estação estiver em uso
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def end_session(self, session_id: int) -> None:
        """
        Finaliza uma sessão de carregamento.
        
        Args:
            session_id: O ID da sessão
            
        Raises:
            ResourceNotFoundError: Se a sessão não existir
            ResourceConflictError: Se a sessão já estiver finalizada
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def pay_session(
        self,
        session_id: int,
        amount: Decimal
    ) -> None:
        """
        Processa o pagamento de uma sessão.
        
        Args:
            session_id: O ID da sessão
            amount: O valor do pagamento em ETH
            
        Raises:
            ResourceNotFoundError: Se a sessão não existir
            ResourceConflictError: Se a sessão já estiver paga
            ValidationError: Se o valor do pagamento for insuficiente
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def reserve_station(
        self,
        user_address: str,
        station_id: int,
        start_time: datetime,
        duration_hours: float
    ) -> int:
        """
        Reserva uma estação de carregamento.
        
        Args:
            user_address: O endereço da carteira do usuário
            station_id: O ID da estação
            start_time: O horário de início da reserva
            duration_hours: A duração da reserva em horas
            
        Returns:
            O ID da reserva criada
            
        Raises:
            ResourceConflictError: Se a estação já estiver reservada
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def cancel_reservation(self, reservation_id: int) -> None:
        """
        Cancela uma reserva de estação.
        
        Args:
            reservation_id: O ID da reserva
            
        Raises:
            ResourceNotFoundError: Se a reserva não existir
            ResourceConflictError: Se a reserva já estiver cancelada
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def is_station_reserved_for_user(
        self,
        station_id: int,
        user_address: str
    ) -> bool:
        """
        Verifica se uma estação está reservada para um usuário.
        
        Args:
            station_id: O ID da estação
            user_address: O endereço da carteira do usuário
            
        Returns:
            True se a estação estiver reservada para o usuário, False caso contrário
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def is_station_reserved_in_period(
        self,
        station_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Verifica se uma estação está reservada em um período.
        
        Args:
            station_id: O ID da estação
            start_time: O início do período
            end_time: O fim do período
            
        Returns:
            True se a estação estiver reservada no período, False caso contrário
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def get_eth_balance(self, address: str) -> Decimal:
        """
        Obtém o saldo ETH de uma carteira.
        
        Args:
            address: O endereço da carteira
            
        Returns:
            O saldo em ETH
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass

    @abstractmethod
    async def verify_signature(
        self,
        message: str,
        signature: str,
        address: str
    ) -> bool:
        """
        Verifica uma assinatura Ethereum.
        
        Args:
            message: A mensagem que foi assinada
            signature: A assinatura a ser verificada
            address: O endereço da carteira que assinou
            
        Returns:
            True se a assinatura for válida, False caso contrário
            
        Raises:
            BlockchainError: Se houver erro na comunicação com a blockchain
        """
        pass 