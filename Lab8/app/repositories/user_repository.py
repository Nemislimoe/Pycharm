from typing import Optional
from app.models.user import User, UserRole


class UserRepository:
    """Відповідає лише за зберігання та доступ до користувачів. Без бізнес-логіки."""

    def __init__(self) -> None:
        self._users: dict[int, User] = {
            1: User(id=1, name="Олена Ковальчук", role=UserRole.EMPLOYEE),
            2: User(id=2, name="Максим Шевченко", role=UserRole.EMPLOYEE),
            3: User(id=3, name="Ірина Бондаренко", role=UserRole.MANAGER),
            4: User(id=4, name="Андрій Мельник", role=UserRole.MANAGER),
        }
        self._next_id = max(self._users.keys()) + 1

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def get_all(self) -> list[User]:
        return list(self._users.values())

    def create(self, name: str, role: UserRole) -> User:
        user = User(id=self._next_id, name=name, role=role)
        self._next_id += 1
        self._users[user.id] = user
        return user
