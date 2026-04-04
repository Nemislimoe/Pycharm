from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_booking_service
from app.exceptions import BookingError
from app.models.booking import BookingStatus
from app.schemas import (
    CreateBookingRequest,
    CreateBookingResponse,
    BookingResponse,
    CancelBookingRequest,
    CancelledBookingInfo,
)
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=CreateBookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Створити бронювання",
    description="""
**Правила:**
- Кімната повинна бути активна
- Немає конфліктів по часу (для employee — завжди; для manager — лише з іншим manager)
- Employee: не більше 2 активних бронювань, max 2 год
- Manager: може витіснити бронювання employee
""",
)
def create_booking(
    payload: CreateBookingRequest,
    service: BookingService = Depends(get_booking_service),
) -> CreateBookingResponse:
    # Запамʼятовуємо активні бронювання до операції, щоб знайти скасовані менеджером
    bookings_before = {
        b.id for b in service.list_bookings()
        if b.status == BookingStatus.ACTIVE
    }

    try:
        new_booking = service.create_booking(
            room_id=payload.room_id,
            user_id=payload.user_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
    except BookingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    # Визначаємо, які бронювання були скасовані (тільки для manager overrides)
    cancelled = [
        CancelledBookingInfo(booking_id=b.id, cancelled_user_id=b.user_id)
        for b in service.list_bookings()
        if b.id in bookings_before and b.status == BookingStatus.CANCELLED
    ]

    message = "Бронювання успішно створено"
    if cancelled:
        message += f"; скасовано конфліктних бронювань: {len(cancelled)}"

    return CreateBookingResponse(
        booking=BookingResponse(
            id=new_booking.id,
            room_id=new_booking.room_id,
            user_id=new_booking.user_id,
            start_time=new_booking.start_time,
            end_time=new_booking.end_time,
            status=new_booking.status,
        ),
        cancelled_bookings=cancelled,
        message=message,
    )


@router.get(
    "",
    response_model=list[BookingResponse],
    summary="Список усіх бронювань",
)
def list_bookings(
    service: BookingService = Depends(get_booking_service),
) -> list[BookingResponse]:
    bookings = service.list_bookings()
    return [
        BookingResponse(
            id=b.id,
            room_id=b.room_id,
            user_id=b.user_id,
            start_time=b.start_time,
            end_time=b.end_time,
            status=b.status,
        )
        for b in bookings
    ]


@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    summary="Скасувати бронювання",
)
def cancel_booking(
    booking_id: int,
    payload: CancelBookingRequest,
    service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    try:
        booking = service.cancel_booking(
            booking_id=booking_id,
            requesting_user_id=payload.requesting_user_id,
        )
    except BookingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return BookingResponse(
        id=booking.id,
        room_id=booking.room_id,
        user_id=booking.user_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status,
    )
