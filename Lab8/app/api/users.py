from fastapi import APIRouter, Depends

from app.dependencies import get_user_repository
from app.repositories.user_repository import UserRepository
from app.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse], summary="Список користувачів")
def list_users(repo: UserRepository = Depends(get_user_repository)) -> list[UserResponse]:
    return [
        UserResponse(id=u.id, name=u.name, role=u.role)
        for u in repo.get_all()
    ]
