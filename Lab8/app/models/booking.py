from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


@dataclass
class Booking:
    id: int
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.ACTIVE
