from dataclasses import dataclass, field


@dataclass
class Room:
    id: int
    name: str
    capacity: int
    is_active: bool = True
