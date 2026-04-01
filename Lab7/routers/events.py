from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import EventCreate, EventRead, AssignRequest
from service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventRead, status_code=201)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    """
    Create a new event.
    - Only Commander can create events for any department.
    - Scientist → Scientific only, Crew → Technical only.
    - If department is Medical, all Scientists automatically receive it as recommended.
    """
    return EventService(db).create_event(data)


@router.get("/", response_model=List[EventRead])
def list_events(db: Session = Depends(get_db)):
    """Return all events sorted by priority and date."""
    from repository import EventRepository
    svc = EventService(db)
    events = EventRepository(db).get_all()
    return svc.get_sorted_events(events)


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    from repository import EventRepository
    from fastapi import HTTPException, status
    event = EventRepository(db).get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")
    return event


@router.post("/assign", response_model=EventRead)
def assign_user_to_event(data: AssignRequest, db: Session = Depends(get_db)):
    """
    Assign a cosmonaut to an event.
    Business rules enforced:
    - No overlapping events at the same datetime.
    - Max 5 participants per event.
    """
    return EventService(db).assign_user(data.user_id, data.event_id)
