from datetime import datetime
from typing import Optional
from app.models.booking import Booking, BookingStatus


class BookingRepository:
    """Відповідає лише за зберігання та базовий доступ до бронювань. Без бізнес-логіки."""

    def __init__(self) -> None:
        self._bookings: dict[int, Booking] = {}
        self._next_id = 1

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        return self._bookings.get(booking_id)

    def get_all(self) -> list[Booking]:
        return list(self._bookings.values())

    def get_active_by_room(self, room_id: int) -> list[Booking]:
        """Повертає всі активні бронювання для конкретної кімнати."""
        return [
            b for b in self._bookings.values()
            if b.room_id == room_id and b.status == BookingStatus.ACTIVE
        ]

    def get_active_by_user(self, user_id: int) -> list[Booking]:
        """Повертає всі активні бронювання для конкретного користувача."""
        return [
            b for b in self._bookings.values()
            if b.user_id == user_id and b.status == BookingStatus.ACTIVE
        ]

    def get_conflicting(self, room_id: int, start_time: datetime, end_time: datetime) -> list[Booking]:
        """Повертає активні бронювання кімнати, що перетинаються з вказаним часовим інтервалом."""
        return [
            b for b in self.get_active_by_room(room_id)
            if b.start_time < end_time and b.end_time > start_time
        ]

    def save(self, booking: Booking) -> Booking:
        self._bookings[booking.id] = booking
        return booking

    def create(
        self,
        room_id: int,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Booking:
        booking = Booking(
            id=self._next_id,
            room_id=room_id,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            status=BookingStatus.ACTIVE,
        )
        self._next_id += 1
        self._bookings[booking.id] = booking
        return booking
