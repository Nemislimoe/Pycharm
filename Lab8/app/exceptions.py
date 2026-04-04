class BookingError(Exception):
    """Базовий клас для помилок бронювання."""


class RoomNotFoundError(BookingError):
    def __init__(self, room_id: int):
        super().__init__(f"Кімнату з ID={room_id} не знайдено.")


class UserNotFoundError(BookingError):
    def __init__(self, user_id: int):
        super().__init__(f"Користувача з ID={user_id} не знайдено.")


class RoomInactiveError(BookingError):
    def __init__(self, room_name: str):
        super().__init__(f"Кімната '{room_name}' неактивна — бронювання заборонено.")


class BookingConflictError(BookingError):
    def __init__(self, conflicting_ids: list[int]):
        ids = ", ".join(map(str, conflicting_ids))
        super().__init__(
            f"Конфлікт бронювання: кімната вже зайнята (бронювання #{ids})."
        )


class EmployeeBookingLimitError(BookingError):
    def __init__(self, current: int, limit: int):
        super().__init__(
            f"Перевищено ліміт бронювань для employee: {current}/{limit} активних."
        )


class EmployeeDurationLimitError(BookingError):
    def __init__(self, duration_hours: float, limit_hours: int):
        super().__init__(
            f"Тривалість бронювання {duration_hours:.1f}г перевищує ліміт {limit_hours}г для employee."
        )


class InvalidTimeRangeError(BookingError):
    def __init__(self):
        super().__init__("Час початку повинен бути раніше за час закінчення.")
