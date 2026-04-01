"""
Service layer — всі бізнес-правила:
  1. Один космонавт не може бути учасником подій, що відбуваються одночасно.
  2. Подія не може мати більше 5 учасників.
  3. Тільки Commander може створювати події для всіх відділів
     (інші ролі — тільки для свого відділу, але відділ прив'язаний до події,
      тому ми перевіряємо роль Creator).
  4. Автоматичне повідомлення: якщо подія створена для Medical,
     всі Scientist-и отримують її у список "рекомендованих подій".
"""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import DepartmentName, RoleName, User, Event
from repository import (
    UserRepository,
    EventRepository,
    DepartmentRepository,
    RoleRepository,
)
from schemas import EventCreate, UserCreate


MAX_PARTICIPANTS = 5

# In-memory store: {scientist_user_id: [event_id, ...]}
_recommended_events: Dict[int, List[int]] = {}


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def create_user(self, data: UserCreate) -> User:
        # validate role exists
        role = self.role_repo.get_by_id(data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id={data.role_id} not found.",
            )
        # username must be unique
        if self.user_repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{data.username}' is already taken.",
            )
        return self.user_repo.add_user(
            username=data.username,
            full_name=data.full_name or "",
            role_id=data.role_id,
        )

    def get_events_for_user(self, user_id: int) -> List[Event]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found.",
            )
        return user.events

    def get_recommended_events_for_user(
        self, user_id: int, event_repo: EventRepository
    ) -> List[Event]:
        ids = _recommended_events.get(user_id, [])
        return [e for eid in ids if (e := event_repo.get_by_id(eid))]


class EventService:
    def __init__(self, db: Session):
        self.event_repo = EventRepository(db)
        self.user_repo = UserRepository(db)
        self.dept_repo = DepartmentRepository(db)

    def create_event(self, data: EventCreate) -> Event:
        # --- Check creator exists ---
        creator = self.user_repo.get_by_id(data.creator_id)
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Creator user with id={data.creator_id} not found.",
            )

        # --- Check department exists ---
        dept = self.dept_repo.get_by_id(data.department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id={data.department_id} not found.",
            )

        # --- Role-based access ---
        # Only Commander can create events for ANY department.
        # Crew and Scientist can only create events for their own department
        # (we treat: if role != Commander, creator must be from the same dept).
        # Since User doesn't have a department field directly, we interpret this as:
        # non-Commander can only create events for the department that matches
        # their role semantics. Specifically:
        #   Scientist  → Scientific dept
        #   Crew       → Technical dept
        #   Commander  → any dept
        role_name = creator.role.name  # RoleName enum

        if role_name != RoleName.COMMANDER:
            allowed_dept: Optional[DepartmentName] = {
                RoleName.SCIENTIST: DepartmentName.SCIENTIFIC,
                RoleName.CREW: DepartmentName.TECHNICAL,
            }.get(role_name)

            if allowed_dept is None or dept.name != allowed_dept:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Role '{role_name}' can only create events for "
                        f"'{allowed_dept}' department. "
                        f"Only Commander can create events for all departments."
                    ),
                )

        # --- Create the event ---
        event = self.event_repo.add_event(
            title=data.title,
            description=data.description or "",
            date=data.date,
            department_id=data.department_id,
        )

        # --- Rule 4: Medical event → notify all Scientists ---
        if dept.name == DepartmentName.MEDICAL:
            scientists = self.user_repo.get_scientists()
            for scientist in scientists:
                _recommended_events.setdefault(scientist.id, [])
                if event.id not in _recommended_events[scientist.id]:
                    _recommended_events[scientist.id].append(event.id)

        return event

    def assign_user(self, user_id: int, event_id: int) -> Event:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found.",
            )

        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id={event_id} not found.",
            )

        # --- Already assigned? ---
        if self.event_repo.is_user_assigned(user_id, event_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already assigned to this event.",
            )

        # --- Rule 2: Max 5 participants ---
        if len(event.participants) >= MAX_PARTICIPANTS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Event already has {MAX_PARTICIPANTS} participants (maximum reached).",
            )

        # --- Rule 1: No overlapping events for the same user ---
        for existing_event in user.events:
            if existing_event.date == event.date and existing_event.id != event_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"User '{user.username}' already has event "
                        f"'{existing_event.title}' at {event.date}. "
                        "Overlapping events are not allowed."
                    ),
                )

        return self.event_repo.assign_user_to_event(user, event)

    def get_events_for_department(self, dept_id: int) -> List[Event]:
        dept = self.dept_repo.get_by_id(dept_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id={dept_id} not found.",
            )
        return dept.events

    def get_sorted_events(self, events: List[Event]) -> List[Event]:
        """
        Sort events by priority (HIGH first) then by date ascending.
        Priority order: HIGH > MEDIUM > LOW
        """
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(
            events,
            key=lambda e: (priority_order.get(e.priority.value, 3), e.date),
        )
