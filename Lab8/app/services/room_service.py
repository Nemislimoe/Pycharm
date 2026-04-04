from app.models.room import Room
from app.repositories.room_repository import RoomRepository
from app.exceptions import RoomNotFoundError, RoomInactiveError


class RoomService:
    """
    Бізнес-логіка для роботи з кімнатами.
    SQL — лише в репозиторії. Правила — тут.
    """

    def __init__(self, room_repo: RoomRepository) -> None:
        self._room_repo = room_repo

    def get_room_or_raise(self, room_id: int) -> Room:
        """Повертає кімнату або піднімає виняток, якщо не знайдено."""
        room = self._room_repo.get_by_id(room_id)
        if room is None:
            raise RoomNotFoundError(room_id)
        return room

    def ensure_room_is_active(self, room: Room) -> None:
        """Перевіряє, що кімната активна, інакше — виняток."""
        if not room.is_active:
            raise RoomInactiveError(room.name)

    def list_rooms(self) -> list[Room]:
        return self._room_repo.get_all()

    def create_room(self, name: str, capacity: int, is_active: bool = True) -> Room:
        return self._room_repo.create(name=name, capacity=capacity, is_active=is_active)

    def deactivate_room(self, room_id: int) -> Room:
        room = self.get_room_or_raise(room_id)
        room.is_active = False
        return self._room_repo.save(room)

    def activate_room(self, room_id: int) -> Room:
        room = self.get_room_or_raise(room_id)
        room.is_active = True
        return self._room_repo.save(room)
