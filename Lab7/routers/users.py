from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserCreate, UserRead, EventRead
from service import UserService, EventService
from repository import EventRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """Create a new cosmonaut (user)."""
    return UserService(db).create_user(data)


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    from repository import UserRepository
    return UserRepository(db).get_all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    from repository import UserRepository
    from fastapi import HTTPException, status
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get("/{user_id}/events", response_model=List[EventRead])
def get_user_events(user_id: int, db: Session = Depends(get_db)):
    """
    Return all events for a given cosmonaut,
    sorted by priority (High → Medium → Low) then by date.
    """
    svc = EventService(db)
    events = UserService(db).get_events_for_user(user_id)
    return svc.get_sorted_events(events)


@router.get("/{user_id}/recommended", response_model=List[EventRead])
def get_recommended_events(user_id: int, db: Session = Depends(get_db)):
    """
    Return the list of recommended Medical events for a Scientist user.
    Populated automatically when a Medical event is created.
    """
    event_repo = EventRepository(db)
    events = UserService(db).get_recommended_events_for_user(user_id, event_repo)
    return EventService(db).get_sorted_events(events)
