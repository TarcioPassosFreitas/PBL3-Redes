from typing import List, Optional
from sqlalchemy.orm import Session
from domain.entities.user import User
from domain.ports.user_repository_port import UserRepositoryPort

class UserRepository(UserRepositoryPort):
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter_by(id=user_id).first()

    def get_by_wallet(self, wallet_address: str) -> Optional[User]:
        return self.db.query(User).filter_by(wallet_address=wallet_address).first()

    def list_all(self) -> List[User]:
        return self.db.query(User).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.merge(user)
        self.db.commit()
        return user

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit() 