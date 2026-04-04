"""
Тести для системи бронювання переговорних кімнат.

Обовʼязкові сценарії:
1. ✅ Успішне бронювання
2. ✅ Відмова через конфлікт
3. ✅ Відмова через перевищення ліміту
4. ✅ Manager перекриває employee
5. ✅ Бронювання неактивної кімнати
"""
import pytest
from datetime import datetime, timedelta

from app.models.user import UserRole
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.services.booking_service import BookingService
from app.services.room_service import RoomService
from app.exceptions import (
    BookingConflictError,
    EmployeeBookingLimitError,
    EmployeeDurationLimitError,
    RoomInactiveError,
    RoomNotFoundError,
    UserNotFoundError,
    InvalidTimeRangeError,
)


# ─────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────

def make_services():
    """Фабрика чистих залежностей для кожного тесту."""
    room_repo = RoomRepository()
    user_repo = UserRepository()
    booking_repo = BookingRepository()
    room_service = RoomService(room_repo=room_repo)
    booking_service = BookingService(
        booking_repo=booking_repo,
        user_repo=user_repo,
        room_service=room_service,
    )
    return booking_service, room_service, room_repo, user_repo, booking_repo


def dt(hour: int, minute: int = 0) -> datetime:
    """Хелпер: datetime сьогодні о вказаній годині."""
    return datetime(2025, 6, 1, hour, minute)


# ─────────────────────────────────────────────────
# Сценарій 1: Успішне бронювання
# ─────────────────────────────────────────────────

class TestSuccessfulBooking:
    def test_employee_books_available_room(self):
        svc, *_ = make_services()
        booking = svc.create_booking(
            room_id=1,
            user_id=1,           # employee
            start_time=dt(9),
            end_time=dt(10),
        )
        assert booking.id is not None
        assert booking.room_id == 1
        assert booking.user_id == 1
        assert booking.status.value == "active"

    def test_manager_books_available_room(self):
        svc, *_ = make_services()
        booking = svc.create_booking(
            room_id=2,
            user_id=3,           # manager
            start_time=dt(14),
            end_time=dt(17),     # 3 год — ОК для manager
        )
        assert booking.status.value == "active"

    def test_two_different_rooms_same_time(self):
        svc, *_ = make_services()
        b1 = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        b2 = svc.create_booking(room_id=2, user_id=2, start_time=dt(9), end_time=dt(10))
        assert b1.status.value == "active"
        assert b2.status.value == "active"

    def test_sequential_bookings_same_room(self):
        """Суміжні (не перекриваються) бронювання однієї кімнати — ОК."""
        svc, *_ = make_services()
        b1 = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        b2 = svc.create_booking(room_id=1, user_id=2, start_time=dt(10), end_time=dt(11))
        assert b1.status.value == "active"
        assert b2.status.value == "active"


# ─────────────────────────────────────────────────
# Сценарій 2: Відмова через конфлікт
# ─────────────────────────────────────────────────

class TestConflictRejection:
    def test_employee_conflict_same_time(self):
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        with pytest.raises(BookingConflictError):
            svc.create_booking(room_id=1, user_id=2, start_time=dt(9), end_time=dt(10))

    def test_employee_conflict_overlap_start(self):
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(11))
        with pytest.raises(BookingConflictError):
            svc.create_booking(room_id=1, user_id=2, start_time=dt(10), end_time=dt(12))

    def test_employee_conflict_overlap_end(self):
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=1, start_time=dt(10), end_time=dt(12))
        with pytest.raises(BookingConflictError):
            svc.create_booking(room_id=1, user_id=2, start_time=dt(9), end_time=dt(11))

    def test_employee_conflict_fully_inside(self):
        """Бронювання всередині вже існуючого — конфлікт."""
        svc, *_ = make_services()
        # Перший employee бронює 9-11 (рівно 2 год — ОК)
        svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(11))
        # Другий employee намагається забронювати 9:30-10:30, що всередині першого
        with pytest.raises(BookingConflictError):
            svc.create_booking(room_id=1, user_id=2, start_time=dt(9, 30), end_time=dt(10, 30))

    def test_manager_vs_manager_conflict_rejected(self):
        """Manager не може витіснити іншого manager."""
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=3, start_time=dt(9), end_time=dt(11))
        with pytest.raises(BookingConflictError):
            svc.create_booking(room_id=1, user_id=4, start_time=dt(10), end_time=dt(12))


# ─────────────────────────────────────────────────
# Сценарій 3: Відмова через перевищення ліміту employee
# ─────────────────────────────────────────────────

class TestEmployeeLimits:
    def test_employee_max_active_bookings(self):
        """Employee не може мати > 2 активних бронювань."""
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        svc.create_booking(room_id=2, user_id=1, start_time=dt(11), end_time=dt(12))
        with pytest.raises(EmployeeBookingLimitError):
            svc.create_booking(room_id=1, user_id=1, start_time=dt(14), end_time=dt(15))

    def test_employee_max_duration_exactly_2h(self):
        """Рівно 2 год — дозволено."""
        svc, *_ = make_services()
        booking = svc.create_booking(
            room_id=1, user_id=1,
            start_time=dt(9), end_time=dt(11),
        )
        assert booking.status.value == "active"

    def test_employee_duration_over_limit(self):
        """Більше 2 год — заборонено."""
        svc, *_ = make_services()
        with pytest.raises(EmployeeDurationLimitError):
            svc.create_booking(
                room_id=1, user_id=1,
                start_time=dt(9), end_time=dt(12),   # 3 год
            )

    def test_employee_duration_2h_1min_rejected(self):
        svc, *_ = make_services()
        with pytest.raises(EmployeeDurationLimitError):
            svc.create_booking(
                room_id=1, user_id=1,
                start_time=datetime(2025, 6, 1, 9, 0),
                end_time=datetime(2025, 6, 1, 11, 1),
            )

    def test_cancelled_booking_not_counted_in_limit(self):
        """Скасоване бронювання не рахується у ліміт."""
        svc, _, _, _, booking_repo = make_services()
        b1 = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        b2 = svc.create_booking(room_id=2, user_id=1, start_time=dt(11), end_time=dt(12))

        # Manager скасовує b1
        svc.cancel_booking(booking_id=b1.id, requesting_user_id=3)

        # Тепер employee має 1 активне — може бронювати ще
        b3 = svc.create_booking(room_id=1, user_id=1, start_time=dt(14), end_time=dt(15))
        assert b3.status.value == "active"

    def test_manager_not_limited_by_count(self):
        """Manager може мати більше 2 активних бронювань."""
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=3, start_time=dt(9), end_time=dt(10))
        svc.create_booking(room_id=2, user_id=3, start_time=dt(11), end_time=dt(12))
        # Третє — ОК для manager (потрібна ще кімната, але кімнат лише 2 активних)
        # Перевіряємо, що ліміту кількості немає (використаємо інший час в тій же кімнаті)
        b3 = svc.create_booking(room_id=1, user_id=3, start_time=dt(11), end_time=dt(12))
        assert b3.status.value == "active"


# ─────────────────────────────────────────────────
# Сценарій 4: Manager перекриває employee
# ─────────────────────────────────────────────────

class TestManagerOverride:
    def test_manager_overrides_employee_booking(self):
        svc, *_ = make_services()
        # Employee бронює кімнату
        emp_booking = svc.create_booking(
            room_id=1, user_id=1,
            start_time=dt(9), end_time=dt(10),
        )
        assert emp_booking.status.value == "active"

        # Manager бронює той самий час — витісняє employee
        mgr_booking = svc.create_booking(
            room_id=1, user_id=3,
            start_time=dt(9), end_time=dt(10),
        )
        assert mgr_booking.status.value == "active"

        # Бронювання employee скасовано
        all_bookings = svc.list_bookings()
        emp_b = next(b for b in all_bookings if b.id == emp_booking.id)
        assert emp_b.status.value == "cancelled"

    def test_manager_overrides_multiple_employee_bookings(self):
        """Manager перекриває кілька бронювань employee одночасно."""
        svc, *_ = make_services()
        # Два employee бронюють послідовні слоти в одній кімнаті
        b1 = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        b2 = svc.create_booking(room_id=1, user_id=2, start_time=dt(10), end_time=dt(11))

        # Manager бронює великий слот, який перекриває обидва (3 год — ОК для manager)
        mgr = svc.create_booking(room_id=1, user_id=3, start_time=dt(9), end_time=dt(12))
        assert mgr.status.value == "active"

        all_b = {b.id: b for b in svc.list_bookings()}
        assert all_b[b1.id].status.value == "cancelled"
        assert all_b[b2.id].status.value == "cancelled"

    def test_manager_cannot_override_another_manager(self):
        svc, *_ = make_services()
        svc.create_booking(room_id=1, user_id=3, start_time=dt(9), end_time=dt(11))
        with pytest.raises(BookingConflictError):
            svc.create_booking(room_id=1, user_id=4, start_time=dt(9), end_time=dt(11))


# ─────────────────────────────────────────────────
# Сценарій 5: Бронювання неактивної кімнати
# ─────────────────────────────────────────────────

class TestInactiveRoom:
    def test_employee_cannot_book_inactive_room(self):
        svc, *_ = make_services()
        with pytest.raises(RoomInactiveError):
            svc.create_booking(room_id=3, user_id=1, start_time=dt(9), end_time=dt(10))

    def test_manager_cannot_book_inactive_room(self):
        """Навіть manager не може бронювати неактивну кімнату."""
        svc, *_ = make_services()
        with pytest.raises(RoomInactiveError):
            svc.create_booking(room_id=3, user_id=3, start_time=dt(9), end_time=dt(10))

    def test_deactivated_room_blocks_new_bookings(self):
        svc, room_svc, *_ = make_services()
        # Спочатку кімната 1 активна
        b1 = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        assert b1.status.value == "active"

        # Деактивуємо кімнату
        room_svc.deactivate_room(1)

        # Нове бронювання заблоковано
        with pytest.raises(RoomInactiveError):
            svc.create_booking(room_id=1, user_id=2, start_time=dt(11), end_time=dt(12))


# ─────────────────────────────────────────────────
# Додаткові: валідація та edge-cases
# ─────────────────────────────────────────────────

class TestEdgeCases:
    def test_nonexistent_room(self):
        svc, *_ = make_services()
        with pytest.raises(RoomNotFoundError):
            svc.create_booking(room_id=999, user_id=1, start_time=dt(9), end_time=dt(10))

    def test_nonexistent_user(self):
        svc, *_ = make_services()
        with pytest.raises(UserNotFoundError):
            svc.create_booking(room_id=1, user_id=999, start_time=dt(9), end_time=dt(10))

    def test_invalid_time_range(self):
        svc, *_ = make_services()
        with pytest.raises(InvalidTimeRangeError):
            svc.create_booking(room_id=1, user_id=1, start_time=dt(11), end_time=dt(9))

    def test_same_start_end_time(self):
        svc, *_ = make_services()
        with pytest.raises(InvalidTimeRangeError):
            svc.create_booking(room_id=1, user_id=1, start_time=dt(10), end_time=dt(10))

    def test_cancel_own_booking_as_employee(self):
        svc, *_ = make_services()
        b = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        cancelled = svc.cancel_booking(booking_id=b.id, requesting_user_id=1)
        assert cancelled.status.value == "cancelled"

    def test_employee_cannot_cancel_others_booking(self):
        from app.exceptions import BookingError
        svc, *_ = make_services()
        b = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        with pytest.raises(BookingError):
            svc.cancel_booking(booking_id=b.id, requesting_user_id=2)

    def test_manager_can_cancel_any_booking(self):
        svc, *_ = make_services()
        b = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        cancelled = svc.cancel_booking(booking_id=b.id, requesting_user_id=3)
        assert cancelled.status.value == "cancelled"

    def test_activated_room_allows_booking_again(self):
        svc, room_svc, *_ = make_services()
        room_svc.deactivate_room(1)
        room_svc.activate_room(1)
        b = svc.create_booking(room_id=1, user_id=1, start_time=dt(9), end_time=dt(10))
        assert b.status.value == "active"
