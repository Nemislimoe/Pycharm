from typing import Optional
from app.models.room import Room


class RoomRepository:
    """Відповідає лише за зберігання та доступ до кімнат. Без бізнес-логіки."""

    def __init__(self) -> None:
        self._rooms: dict[int, Room] = {
            1: Room(id=1, name="Конференц-зал A", capacity=10, is_active=True),
            2: Room(id=2, name="Переговорна B", capacity=4, is_active=True),
            3: Room(id=3, name="Велика зала C", capacity=20, is_active=False),
        }
        self._next_id = max(self._rooms.keys()) + 1

    def get_by_id(self, room_id: int) -> Optional[Room]:
        return self._rooms.get(room_id)

    def get_all(self) -> list[Room]:
        return list(self._rooms.values())

    def save(self, room: Room) -> Room:
        self._rooms[room.id] = room
        return room

    def create(self, name: str, capacity: int, is_active: bool = True) -> Room:
        room = Room(id=self._next_id, name=name, capacity=capacity, is_active=is_active)
        self._next_id += 1
        self._rooms[room.id] = room
        return room
