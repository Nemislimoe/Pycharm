from fastapi import FastAPI, Query
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

app = FastAPI()


# ════════════════════════════════════════════════════════
# Завдання 1. POST /users/register
# ════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    email:     EmailStr
    password:  str       = Field(min_length=8)
    age:       int       = Field(ge=14)
    is_active: bool      = True


class UserResponse(BaseModel):
    id:        int
    email:     EmailStr
    age:       int
    is_active: bool
    # ⚠️  password навмисно відсутній — не повертаємо його клієнту


# Простий лічильник для генерації id
_user_counter = 0

@app.post("/users/register", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate):
    global _user_counter
    _user_counter += 1
    return UserResponse(
        id=_user_counter,
        email=user.email,
        age=user.age,
        is_active=user.is_active,
    )


# ════════════════════════════════════════════════════════
# Завдання 2. GET /products
# ════════════════════════════════════════════════════════

@app.get("/products")
def get_products(
    page:   int            = Query(default=1,  ge=1),
    limit:  int            = Query(default=10, ge=1, le=100),
    search: Optional[str]  = Query(default=None, min_length=3),
):
    # Тут буде логіка пошуку/пагінації; зараз повертаємо порожній список
    return {
        "page":   page,
        "limit":  limit,
        "search": search,
        "items":  [],
    }


# ════════════════════════════════════════════════════════
# Завдання 3. POST /feedback
# ════════════════════════════════════════════════════════

class FeedbackCreate(BaseModel):
    name:    str           = Field(min_length=2)
    email:   EmailStr
    rating:  int           = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=200)


class FeedbackResponse(FeedbackCreate):
    message: str = "Thank you for your feedback!"


@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
def create_feedback(feedback: FeedbackCreate):
    return FeedbackResponse(**feedback.model_dump())