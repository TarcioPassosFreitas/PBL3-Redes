from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class SessionStatus(Enum):
    """
    Enumeração que representa os possíveis estados de uma sessão de carregamento.
    """
    PENDING = "pending"  # Sessão aguardando início
    ACTIVE = "active"    # Sessão em andamento
    COMPLETED = "completed"  # Sessão finalizada
    PAID = "paid"        # Sessão paga
    CANCELLED = "cancelled"  # Sessão cancelada


class Session:
    """
    Entidade que representa uma sessão de carregamento.
    Armazena informações sobre a sessão, incluindo seu estado e dados de pagamento.
    """

    def __init__(
        self,
        id: int,
        user_address: str,
        station_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: SessionStatus = SessionStatus.PENDING,
        payment_amount: Optional[Decimal] = None,
        payment_time: Optional[datetime] = None
    ):
        """
        Inicializa uma nova sessão.
        
        Args:
            id: O ID único da sessão
            user_address: O endereço da carteira do usuário
            station_id: O ID da estação de carregamento
            start_time: O horário de início da sessão
            end_time: O horário de fim da sessão
            status: O estado atual da sessão
            payment_amount: O valor do pagamento em ETH
            payment_time: O horário do pagamento
        """
        self.id = id
        self.user_address = user_address
        self.station_id = station_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.payment_amount = payment_amount
        self.payment_time = payment_time

    def start(self) -> None:
        """
        Inicia a sessão de carregamento.
        Define o horário de início e atualiza o estado para ativo.
        """
        self.start_time = datetime.utcnow()
        self.status = SessionStatus.ACTIVE

    def end(self) -> None:
        """
        Finaliza a sessão de carregamento.
        Define o horário de fim e atualiza o estado para completado.
        """
        self.end_time = datetime.utcnow()
        self.status = SessionStatus.COMPLETED

    def pay(self, amount: Decimal) -> None:
        """
        Registra o pagamento da sessão.
        
        Args:
            amount: O valor do pagamento em ETH
        """
        self.payment_amount = amount
        self.payment_time = datetime.utcnow()
        self.status = SessionStatus.PAID

    def cancel(self) -> None:
        """
        Cancela a sessão de carregamento.
        Atualiza o estado para cancelado.
        """
        self.status = SessionStatus.CANCELLED

    def get_duration(self) -> Optional[float]:
        """
        Calcula a duração da sessão em horas.
        
        Returns:
            A duração em horas, ou None se a sessão não tiver sido finalizada
        """
        if not self.start_time or not self.end_time:
            return None

        duration = (self.end_time - self.start_time).total_seconds()
        return duration / 3600  # Converte segundos para horas

    def to_dict(self) -> dict:
        """
        Converte a sessão para um dicionário.
        
        Returns:
            Um dicionário com os dados da sessão
        """
        return {
            "id": self.id,
            "user_address": self.user_address,
            "station_id": self.station_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "payment_amount": str(self.payment_amount) if self.payment_amount else None,
            "payment_time": self.payment_time.isoformat() if self.payment_time else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """
        Cria uma sessão a partir de um dicionário.
        
        Args:
            data: O dicionário com os dados da sessão
            
        Returns:
            Uma nova instância de Session
        """
        return cls(
            id=data["id"],
            user_address=data["user_address"],
            station_id=data["station_id"],
            start_time=datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            status=SessionStatus(data["status"]),
            payment_amount=Decimal(data["payment_amount"]) if data["payment_amount"] else None,
            payment_time=datetime.fromisoformat(data["payment_time"]) if data["payment_time"] else None
        ) 