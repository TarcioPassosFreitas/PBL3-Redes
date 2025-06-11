from domain.ports.user_repository_port import UserRepositoryPort
from domain.dto.user_dto import UserDTO

class UserUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def get_user(self, user_id: int):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        return UserDTO.from_entity(user).to_dict()

    def list_users(self):
        users = self.user_repository.list_all()
        return [UserDTO.from_entity(u).to_dict() for u in users]

    def create_user(self, user_data):
        # user_data: dict
        from domain.entities.user import User
        import datetime
        user = User(
            id=None,
            wallet_address=user_data["wallet_address"],
            email=user_data["email"],
            name=user_data["name"],
            created_at=datetime.datetime.utcnow(),
            last_login=None
        )
        user = self.user_repository.create(user)
        return UserDTO.from_entity(user).to_dict()

    def update_user(self, user_id, user_data):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        for k, v in user_data.items():
            setattr(user, k, v)
        user = self.user_repository.update(user)
        return UserDTO.from_entity(user).to_dict()

    def delete_user(self, user_id):
        self.user_repository.delete(user_id)
        return {"deleted": True} 