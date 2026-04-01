from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import DepartmentCreate, DepartmentRead, EventRead
from repository import DepartmentRepository
from service import EventService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentRead, status_code=201)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    """Create a department (Scientific / Technical / Medical)."""
    repo = DepartmentRepository(db)
    existing = next((d for d in repo.get_all() if d.name == data.name), None)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department '{data.name}' already exists.",
        )
    return repo.create(name=data.name, description=data.description or "")


@router.get("/", response_model=List[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    return DepartmentRepository(db).get_all()


@router.get("/{dept_id}/events", response_model=List[EventRead])
def get_department_events(dept_id: int, db: Session = Depends(get_db)):
    """
    Return all events for a department,
    sorted by priority (High → Medium → Low) then by date.
    """
    svc = EventService(db)
    events = svc.get_events_for_department(dept_id)
    return svc.get_sorted_events(events)
