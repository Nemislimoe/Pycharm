from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_room_service
from app.exceptions import BookingError
from app.schemas import RoomResponse, CreateRoomRequest
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("", response_model=list[RoomResponse], summary="Список кімнат")
def list_rooms(service: RoomService = Depends(get_room_service)) -> list[RoomResponse]:
    return [
        RoomResponse(id=r.id, name=r.name, capacity=r.capacity, is_active=r.is_active)
        for r in service.list_rooms()
    ]


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Створити кімнату",
)
def create_room(
    payload: CreateRoomRequest,
    service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    room = service.create_room(
        name=payload.name,
        capacity=payload.capacity,
        is_active=payload.is_active,
    )
    return RoomResponse(id=room.id, name=room.name, capacity=room.capacity, is_active=room.is_active)


@router.patch(
    "/{room_id}/deactivate",
    response_model=RoomResponse,
    summary="Деактивувати кімнату",
)
def deactivate_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    try:
        room = service.deactivate_room(room_id)
    except BookingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return RoomResponse(id=room.id, name=room.name, capacity=room.capacity, is_active=room.is_active)


@router.patch(
    "/{room_id}/activate",
    response_model=RoomResponse,
    summary="Активувати кімнату",
)
def activate_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
) -> RoomResponse:
    try:
        room = service.activate_room(room_id)
    except BookingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return RoomResponse(id=room.id, name=room.name, capacity=room.capacity, is_active=room.is_active)
