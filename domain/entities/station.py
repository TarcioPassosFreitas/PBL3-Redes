from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional


class Station:
    """
    Entidade que representa uma estação de carregamento.
    Armazena informações sobre a estação e seu estado atual.
    """

    def __init__(
        self,
        id: int,
        location: str,
        power_output: Decimal,
        price_per_hour: Decimal,
        is_available: bool = True,
        current_session_id: Optional[int] = None,
        reservations: Optional[Dict[str, List[Dict[str, any]]]] = None,
        total_sessions: int = 0,
        total_revenue: Decimal = Decimal('0')
    ):
        """
        Inicializa uma nova estação.
        
        Args:
            id: O ID único da estação
            location: A localização da estação
            power_output: A potência de saída em kW
            price_per_hour: O preço por hora em ETH
            is_available: Se a estação está disponível
            current_session_id: O ID da sessão atual, se houver
            reservations: Dicionário de reservas por data
            total_sessions: Total de sessões realizadas
            total_revenue: Receita total em ETH
        """
        self.id = id
        self.location = location
        self.power_output = power_output
        self.price_per_hour = price_per_hour
        self.is_available = is_available
        self.current_session_id = current_session_id
        self.reservations = reservations or {}
        self.total_sessions = total_sessions
        self.total_revenue = total_revenue

    def add_reservation(
        self,
        user_address: str,
        start_time: datetime,
        end_time: datetime
    ) -> None:
        """
        Adiciona uma reserva para a estação.
        
        Args:
            user_address: O endereço da carteira do usuário
            start_time: O horário de início da reserva
            end_time: O horário de fim da reserva
        """
        date_key = start_time.strftime("%Y-%m-%d")
        if date_key not in self.reservations:
            self.reservations[date_key] = []

        self.reservations[date_key].append({
            "user_address": user_address,
            "start_time": start_time,
            "end_time": end_time
        })

    def remove_reservation(
        self,
        user_address: str,
        start_time: datetime,
        end_time: datetime
    ) -> None:
        """
        Remove uma reserva da estação.
        
        Args:
            user_address: O endereço da carteira do usuário
            start_time: O horário de início da reserva
            end_time: O horário de fim da reserva
        """
        date_key = start_time.strftime("%Y-%m-%d")
        if date_key in self.reservations:
            self.reservations[date_key] = [
                r for r in self.reservations[date_key]
                if not (
                    r["user_address"] == user_address and
                    r["start_time"] == start_time and
                    r["end_time"] == end_time
                )
            ]

    def is_reserved_at(self, time: datetime) -> bool:
        """
        Verifica se a estação está reservada em um horário específico.
        
        Args:
            time: O horário a ser verificado
            
        Returns:
            True se a estação estiver reservada, False caso contrário
        """
        date_key = time.strftime("%Y-%m-%d")
        if date_key not in self.reservations:
            return False

        return any(
            r["start_time"] <= time <= r["end_time"]
            for r in self.reservations[date_key]
        )

    def get_reservation_user(self, time: datetime) -> Optional[str]:
        """
        Obtém o endereço do usuário que tem reserva em um horário específico.
        
        Args:
            time: O horário a ser verificado
            
        Returns:
            O endereço da carteira do usuário com reserva, ou None se não houver
        """
        date_key = time.strftime("%Y-%m-%d")
        if date_key not in self.reservations:
            return None

        for reservation in self.reservations[date_key]:
            if reservation["start_time"] <= time <= reservation["end_time"]:
                return reservation["user_address"]

        return None

    def start_session(self, session_id: int) -> None:
        """
        Inicia uma nova sessão na estação.
        
        Args:
            session_id: O ID da sessão a ser iniciada
        """
        self.is_available = False
        self.current_session_id = session_id

    def end_session(self) -> None:
        """
        Finaliza a sessão atual da estação.
        """
        self.is_available = True
        self.current_session_id = None
        self.total_sessions += 1

    def add_revenue(self, amount: Decimal) -> None:
        """
        Adiciona receita à estação.
        
        Args:
            amount: O valor a ser adicionado em ETH
        """
        self.total_revenue += amount

    def to_dict(self) -> dict:
        """
        Converte a estação para um dicionário.
        
        Returns:
            Um dicionário com os dados da estação
        """
        return {
            "id": self.id,
            "location": self.location,
            "power_output": str(self.power_output),
            "price_per_hour": str(self.price_per_hour),
            "is_available": self.is_available,
            "current_session_id": self.current_session_id,
            "reservations": {
                date: [
                    {
                        "user_address": r["user_address"],
                        "start_time": r["start_time"].isoformat(),
                        "end_time": r["end_time"].isoformat()
                    }
                    for r in reservations
                ]
                for date, reservations in self.reservations.items()
            },
            "total_sessions": self.total_sessions,
            "total_revenue": str(self.total_revenue)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Station':
        """
        Cria uma estação a partir de um dicionário.
        
        Args:
            data: O dicionário com os dados da estação
            
        Returns:
            Uma nova instância de Station
        """
        reservations = {}
        for date, date_reservations in data["reservations"].items():
            reservations[date] = [
                {
                    "user_address": r["user_address"],
                    "start_time": datetime.fromisoformat(r["start_time"]),
                    "end_time": datetime.fromisoformat(r["end_time"])
                }
                for r in date_reservations
            ]

        return cls(
            id=data["id"],
            location=data["location"],
            power_output=Decimal(data["power_output"]),
            price_per_hour=Decimal(data["price_per_hour"]),
            is_available=data["is_available"],
            current_session_id=data["current_session_id"],
            reservations=reservations,
            total_sessions=data["total_sessions"],
            total_revenue=Decimal(data["total_revenue"])
        ) 