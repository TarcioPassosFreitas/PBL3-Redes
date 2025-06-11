from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_wallet(self, wallet_address: str) -> Optional[User]:
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass 