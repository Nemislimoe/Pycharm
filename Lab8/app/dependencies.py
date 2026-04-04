"""
Dependency Injection через FastAPI Depends.
Всі залежності — синглтони на рівні застосунку (in-memory сховища).
"""
from functools import lru_cache
from fastapi import Depends

from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.repositories.booking_repository import BookingRepository
from app.services.room_service import RoomService
from app.services.booking_service import BookingService


# ── Singletons ────────────────────────────────────

@lru_cache
def get_room_repository() -> RoomRepository:
    return RoomRepository()


@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository()


@lru_cache
def get_booking_repository() -> BookingRepository:
    return BookingRepository()


# ── Services ──────────────────────────────────────

def get_room_service(
    room_repo: RoomRepository = Depends(get_room_repository),
) -> RoomService:
    return RoomService(room_repo=room_repo)


def get_booking_service(
    booking_repo: BookingRepository = Depends(get_booking_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    room_service: RoomService = Depends(get_room_service),
) -> BookingService:
    return BookingService(
        booking_repo=booking_repo,
        user_repo=user_repo,
        room_service=room_service,
    )
