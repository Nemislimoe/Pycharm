from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import RoleCreate, RoleRead
from repository import RoleRepository

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleRead, status_code=201)
def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    if repo.get_by_name(data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role '{data.name}' already exists.",
        )
    return repo.create(name=data.name, description=data.description or "")


@router.get("/", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    return RoleRepository(db).get_all()
