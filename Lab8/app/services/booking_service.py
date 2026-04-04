from datetime import datetime

from app.models.booking import Booking, BookingStatus
from app.models.user import UserRole
from app.repositories.booking_repository import BookingRepository
from app.repositories.user_repository import UserRepository
from app.services.room_service import RoomService
from app.exceptions import (
    UserNotFoundError,
    BookingConflictError,
    EmployeeBookingLimitError,
    EmployeeDurationLimitError,
    InvalidTimeRangeError,
)

EMPLOYEE_MAX_ACTIVE_BOOKINGS = 2
EMPLOYEE_MAX_DURATION_HOURS = 2


class BookingService:
    """
    Уся бізнес-логіка бронювання.
    SQL — лише в репозиторіях. Ролі — тільки тут, не в репозиторіях.
    """

    def __init__(
        self,
        booking_repo: BookingRepository,
        user_repo: UserRepository,
        room_service: RoomService,
    ) -> None:
        self._booking_repo = booking_repo
        self._user_repo = user_repo
        self._room_service = room_service

    # ──────────────────────────────────────────────
    # Main use-case: Create Booking
    # ──────────────────────────────────────────────

    def create_booking(
        self,
        room_id: int,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Booking:
        """
        Flow:
        1. Валідація часового діапазону
        2. Перевірка існування кімнати та її активності (через RoomService)
        3. Перевірка існування користувача
        4. Пошук конфліктів
        5. Застосування правил за роллю
           - employee: перевірка лімітів; конфлікт → виняток
           - manager:  може скасувати бронювання employee; manager vs manager → виняток
        6. Збереження нового бронювання
        """

        # 1. Базова валідація часу
        self._validate_time_range(start_time, end_time)

        # 2. Кімната існує та активна
        room = self._room_service.get_room_or_raise(room_id)
        self._room_service.ensure_room_is_active(room)

        # 3. Користувач існує
        user = self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        # 4. Конфлікти
        conflicts = self._booking_repo.get_conflicting(room_id, start_time, end_time)

        # 5. Правила за роллю
        if user.role == UserRole.EMPLOYEE:
            self._apply_employee_rules(user_id, start_time, end_time, conflicts)
        else:
            self._apply_manager_rules(conflicts)

        # 6. Зберігаємо
        return self._booking_repo.create(
            room_id=room_id,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
        )

    # ──────────────────────────────────────────────
    # Cancel Booking
    # ──────────────────────────────────────────────

    def cancel_booking(self, booking_id: int, requesting_user_id: int) -> Booking:
        """
        Скасовує бронювання.
        Employee може скасувати лише своє.
        Manager може скасувати будь-яке.
        """
        from app.exceptions import BookingError

        booking = self._booking_repo.get_by_id(booking_id)
        if booking is None:
            raise BookingError(f"Бронювання #{booking_id} не знайдено.")

        if booking.status == BookingStatus.CANCELLED:
            raise BookingError(f"Бронювання #{booking_id} вже скасовано.")

        user = self._user_repo.get_by_id(requesting_user_id)
        if user is None:
            raise UserNotFoundError(requesting_user_id)

        if user.role == UserRole.EMPLOYEE and booking.user_id != requesting_user_id:
            raise BookingError("Employee може скасувати лише власне бронювання.")

        booking.status = BookingStatus.CANCELLED
        return self._booking_repo.save(booking)

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────

    def list_bookings(self) -> list[Booking]:
        return self._booking_repo.get_all()

    def get_user_bookings(self, user_id: int) -> list[Booking]:
        return self._booking_repo.get_active_by_user(user_id)

    # ──────────────────────────────────────────────
    # Private: rule enforcement
    # ──────────────────────────────────────────────

    def _validate_time_range(self, start_time: datetime, end_time: datetime) -> None:
        if start_time >= end_time:
            raise InvalidTimeRangeError()

    def _apply_employee_rules(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        conflicts: list[Booking],
    ) -> None:
        """
        Employee:
        · Не більше 2 активних бронювань
        · Максимум 2 години на одне бронювання
        · Конфлікти — заборонено
        """
        # Перевірка тривалості
        duration_hours = (end_time - start_time).total_seconds() / 3600
        if duration_hours > EMPLOYEE_MAX_DURATION_HOURS:
            raise EmployeeDurationLimitError(duration_hours, EMPLOYEE_MAX_DURATION_HOURS)

        # Перевірка кількості активних бронювань
        active = self._booking_repo.get_active_by_user(user_id)
        if len(active) >= EMPLOYEE_MAX_ACTIVE_BOOKINGS:
            raise EmployeeBookingLimitError(len(active), EMPLOYEE_MAX_ACTIVE_BOOKINGS)

        # Конфлікт → відмова
        if conflicts:
            raise BookingConflictError([b.id for b in conflicts])

    def _apply_manager_rules(self, conflicts: list[Booking]) -> None:
        """
        Manager:
        · Може перекрити бронювання employee (→ cancelled)
        · Не може перекрити бронювання іншого manager
        """
        if not conflicts:
            return

        for conflict in conflicts:
            conflict_owner = self._user_repo.get_by_id(conflict.user_id)

            # Manager vs manager → конфлікт залишається конфліктом
            if conflict_owner and conflict_owner.role == UserRole.MANAGER:
                raise BookingConflictError([b.id for b in conflicts])

            # Manager vs employee → скасовуємо бронювання employee
            conflict.status = BookingStatus.CANCELLED
            self._booking_repo.save(conflict)
