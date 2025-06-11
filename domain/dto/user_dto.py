from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserDTO:
    id: int
    wallet_address: str
    email: str
    name: str
    created_at: str
    last_login: Optional[str] = None

    @staticmethod
    def from_entity(user):
        return UserDTO(
            id=user.id,
            wallet_address=user.wallet_address,
            email=user.email,
            name=user.name,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )

    def to_dict(self):
        return self.__dict__ 