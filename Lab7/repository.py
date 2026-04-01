from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models import User, Event, Department, Role, DepartmentName


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: str = "") -> Role:
        role = Role(name=name, description=description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def get_all(self) -> List[Role]:
        return self.db.query(Role).all()


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: str = "") -> Department:
        dept = Department(name=name, description=description)
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept

    def get_by_id(self, dept_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == dept_id).first()

    def get_all(self) -> List[Department]:
        return self.db.query(Department).all()

    def get_events_for_department(self, dept_id: int) -> List[Event]:
        """Return all events belonging to a department."""
        dept = self.get_by_id(dept_id)
        if not dept:
            return []
        return dept.events


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_user(self, username: str, full_name: str, role_id: int) -> User:
        user = User(username=username, full_name=full_name, role_id=role_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def get_events_for_user(self, user_id: int) -> List[Event]:
        """Return all events the user is a participant of."""
        user = self.get_by_id(user_id)
        if not user:
            return []
        return user.events

    def get_scientists(self) -> List[User]:
        """Return all users with the Scientist role."""
        return (
            self.db.query(User)
            .join(Role, User.role_id == Role.id)
            .filter(Role.name == "Scientist")
            .all()
        )


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_event(
        self,
        title: str,
        description: str,
        date: datetime,
        department_id: int,
    ) -> Event:
        event = Event(
            title=title,
            description=description,
            date=date,
            department_id=department_id,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_all(self) -> List[Event]:
        return self.db.query(Event).all()

    def assign_user_to_event(self, user: User, event: Event) -> Event:
        """Append user to event participants and persist."""
        event.participants.append(user)
        self.db.commit()
        self.db.refresh(event)
        return event

    def is_user_assigned(self, user_id: int, event_id: int) -> bool:
        event = self.get_by_id(event_id)
        if not event:
            return False
        return any(u.id == user_id for u in event.participants)
