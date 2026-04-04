from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator
from app.models.booking import BookingStatus
from app.models.user import UserRole


# ── Request schemas ──────────────────────────────

class CreateBookingRequest(BaseModel):
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def end_after_start(self) -> "CreateBookingRequest":
        if self.start_time >= self.end_time:
            raise ValueError("end_time повинен бути пізніше за start_time")
        return self


class CancelBookingRequest(BaseModel):
    requesting_user_id: int


class CreateRoomRequest(BaseModel):
    name: str
    capacity: int
    is_active: bool = True


# ── Response schemas ─────────────────────────────

class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    is_active: bool

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole

    model_config = {"from_attributes": True}


class BookingResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus

    model_config = {"from_attributes": True}


class CancelledBookingInfo(BaseModel):
    booking_id: int
    cancelled_user_id: int


class CreateBookingResponse(BaseModel):
    booking: BookingResponse
    cancelled_bookings: list[CancelledBookingInfo] = []
    message: str = "Бронювання успішно створено"
