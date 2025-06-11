from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


@dataclass
class User:
    """
    Entidade que representa um usuário do sistema.
    Armazena informações sobre o usuário e suas interações com o sistema.
    """
    id: int
    wallet_address: str
    email: str
    name: str
    created_at: datetime
    last_login: Optional[datetime] = None
    active_sessions: List[int]  # List of active session IDs
    total_charges: Decimal  # Total amount spent in ETH
    total_sessions: int
    active_reservations: List[int]  # List of active reservation IDs

    def add_session(self, session_id: int) -> None:
        """
        Adiciona uma sessão à lista de sessões ativas.
        
        Args:
            session_id: O ID da sessão a ser adicionada
        """
        if session_id not in self.active_sessions:
            self.active_sessions.append(session_id)

    def remove_session(self, session_id: int) -> None:
        """
        Remove uma sessão da lista de sessões ativas.
        
        Args:
            session_id: O ID da sessão a ser removida
        """
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)

    def update_last_login(self) -> None:
        """
        Update the user's last login timestamp.
        """
        self.last_login = datetime.utcnow()

    def add_charge(self, amount: Decimal) -> None:
        """
        Adiciona um valor de carregamento ao total do usuário.
        
        Args:
            amount: O valor a ser adicionado em ETH
        """
        self.total_charges += amount
        self.total_sessions += 1

    def add_reservation(self, reservation_id: int) -> None:
        """
        Adiciona uma reserva à lista de reservas ativas.
        
        Args:
            reservation_id: O ID da reserva a ser adicionada
        """
        if reservation_id not in self.active_reservations:
            self.active_reservations.append(reservation_id)

    def remove_reservation(self, reservation_id: int) -> None:
        """
        Remove uma reserva da lista de reservas ativas.
        
        Args:
            reservation_id: O ID da reserva a ser removida
        """
        if reservation_id in self.active_reservations:
            self.active_reservations.remove(reservation_id)

    def to_dict(self) -> dict:
        """
        Converte o usuário para um dicionário.
        
        Returns:
            Um dicionário com os dados do usuário
        """
        return {
            "id": self.id,
            "wallet_address": self.wallet_address,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "active_sessions": self.active_sessions,
            "total_charges": str(self.total_charges),
            "total_sessions": self.total_sessions,
            "active_reservations": self.active_reservations
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Cria um usuário a partir de um dicionário.
        
        Args:
            data: O dicionário com os dados do usuário
            
        Returns:
            Uma nova instância de User
        """
        return cls(
            id=data["id"],
            wallet_address=data["wallet_address"],
            email=data["email"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            active_sessions=data["active_sessions"],
            total_charges=Decimal(data["total_charges"]),
            total_sessions=data["total_sessions"],
            active_reservations=data["active_reservations"]
        )

    @classmethod
    def create_new(cls, wallet_address: str, email: Optional[str] = None, name: Optional[str] = None) -> 'User':
        """
        Create a new user instance.
        """
        return cls(
            id=0,  # Assuming a default id
            wallet_address=wallet_address,
            email=email,
            name=name,
            created_at=datetime.utcnow(),
            last_login=None,
            active_sessions=[],
            total_charges=Decimal('0'),
            total_sessions=0,
            active_reservations=[]
        ) 