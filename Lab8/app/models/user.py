from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"


@dataclass
class User:
    id: int
    name: str
    role: UserRole
