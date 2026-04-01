from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Table, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum

from database import Base

# ──────────────────────────────────────────────
# Enum types
# ──────────────────────────────────────────────

class RoleName(str, enum.Enum):
    CREW = "Crew"
    COMMANDER = "Commander"
    SCIENTIST = "Scientist"


class DepartmentName(str, enum.Enum):
    SCIENTIFIC = "Scientific"
    TECHNICAL = "Technical"
    MEDICAL = "Medical"


class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


# ──────────────────────────────────────────────
# Association table: User ↔ Event (Many-to-Many)
# ──────────────────────────────────────────────

user_event = Table(
    "user_event",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
)


# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SAEnum(RoleName), unique=True, nullable=False)
    description = Column(Text, default="")

    users = relationship("User", back_populates="role")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SAEnum(DepartmentName), unique=True, nullable=False)
    description = Column(Text, default="")

    events = relationship("Event", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200), default="")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    events = relationship("Event", secondary=user_event, back_populates="participants")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    date = Column(DateTime, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    department = relationship("Department", back_populates="events")
    participants = relationship("User", secondary=user_event, back_populates="events")

    @property
    def priority(self) -> Priority:
        count = len(self.participants)
        if count > 3:
            return Priority.HIGH
        elif count >= 2:
            return Priority.MEDIUM
        elif count == 1:
            return Priority.LOW
        return Priority.LOW
