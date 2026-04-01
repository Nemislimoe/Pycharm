from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from models import Priority, RoleName, DepartmentName


# ──────────────────────────────────────────────
# Role schemas
# ──────────────────────────────────────────────

class RoleBase(BaseModel):
    name: RoleName
    description: Optional[str] = ""


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ──────────────────────────────────────────────
# Department schemas
# ──────────────────────────────────────────────

class DepartmentBase(BaseModel):
    name: DepartmentName
    description: Optional[str] = ""


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ──────────────────────────────────────────────
# User schemas
# ──────────────────────────────────────────────

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = ""


class UserCreate(UserBase):
    role_id: int


class UserShort(BaseModel):
    """Compact user info embedded inside Event responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: Optional[str] = ""


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: RoleRead


# ──────────────────────────────────────────────
# Event schemas
# ──────────────────────────────────────────────

class EventBase(BaseModel):
    title: str
    description: Optional[str] = ""
    date: datetime
    department_id: int


class EventCreate(EventBase):
    creator_id: int  # user who creates the event (must be Commander for cross-dept)


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department: DepartmentRead
    participants: List[UserShort] = []
    priority: Priority


# ──────────────────────────────────────────────
# Assignment schema
# ──────────────────────────────────────────────

class AssignRequest(BaseModel):
    user_id: int
    event_id: int


# ──────────────────────────────────────────────
# Recommended events (for Scientists when Medical event created)
# ──────────────────────────────────────────────

class RecommendedEventsRead(BaseModel):
    user_id: int
    username: str
    recommended_events: List[EventRead]
