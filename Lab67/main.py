from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
import uuid
import math

app = FastAPI(
    title="📚 Менеджер книжкової колекції",
    description="REST API для управління колекцією книжок з валідацією через Pydantic",
    version="1.0.0",
)

# ─────────────────────────────────────────────
# In-memory storage
# ─────────────────────────────────────────────
books_db: dict[str, dict] = {}

CURRENT_YEAR = datetime.now().year

VALID_TAGS = {
    "класика", "фантастика", "навчальна", "детектив", "роман",
    "пригоди", "поезія", "біографія", "наукова", "філософія",
    "психологія", "жахи", "трилер", "гумор", "дитяча",
}


# ─────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────
class BookCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Назва книги (3–100 символів)",
        examples=["Майстер і Маргарита"],
    )
    author: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Автор книги (3–50 символів)",
        examples=["Михайло Булгаков"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Опис книги (до 500 символів)",
    )
    year: Optional[int] = Field(
        None,
        description=f"Рік видання (1450–{CURRENT_YEAR})",
        examples=[1967],
    )
    rating: Optional[float] = Field(
        None,
        description="Оцінка книги (0.0–5.0, один десятковий знак)",
        examples=[4.5],
    )
    tags: Optional[list[str]] = Field(
        default_factory=list,
        description=f"Теги книги. Допустимі значення: {', '.join(sorted(VALID_TAGS))}",
    )

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if v is not None and not (1450 <= v <= CURRENT_YEAR):
            raise ValueError(f"Рік видання має бути між 1450 та {CURRENT_YEAR}")
        return v

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v is not None:
            if not (0.0 <= v <= 5.0):
                raise ValueError("Оцінка має бути від 0 до 5")
            # Round to 1 decimal place and check it was already 1dp
            rounded = round(v, 1)
            if not math.isclose(v, rounded):
                raise ValueError("Оцінка може мати максимум 1 десятковий знак")
            return rounded
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v:
            invalid = [t for t in v if t.lower() not in VALID_TAGS]
            if invalid:
                raise ValueError(
                    f"Недопустимі теги: {invalid}. "
                    f"Дозволені: {sorted(VALID_TAGS)}"
                )
            return [t.lower() for t in v]
        return v or []

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip()


class BookUpdate(BaseModel):
    """Схема оновлення — всі поля необов'язкові."""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    author: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    year: Optional[int] = None
    rating: Optional[float] = None
    tags: Optional[list[str]] = None

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if v is not None and not (1450 <= v <= CURRENT_YEAR):
            raise ValueError(f"Рік видання має бути між 1450 та {CURRENT_YEAR}")
        return v

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v is not None:
            if not (0.0 <= v <= 5.0):
                raise ValueError("Оцінка має бути від 0 до 5")
            rounded = round(v, 1)
            if not math.isclose(v, rounded):
                raise ValueError("Оцінка може мати максимум 1 десятковий знак")
            return rounded
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            invalid = [t for t in v if t.lower() not in VALID_TAGS]
            if invalid:
                raise ValueError(
                    f"Недопустимі теги: {invalid}. "
                    f"Дозволені: {sorted(VALID_TAGS)}"
                )
            return [t.lower() for t in v]
        return v

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if v else v


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str]
    year: Optional[int]
    rating: Optional[float]
    tags: list[str]


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────
def get_book_or_404(book_id: str) -> dict:
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Книгу з id '{book_id}' не знайдено")
    return book


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.post(
    "/books/",
    response_model=BookResponse,
    status_code=201,
    summary="Створити книгу",
    tags=["Книги"],
)
def create_book(book: BookCreate):
    """
    Створює нову книгу та додає її до колекції.

    - **title**: обов'язкова назва (3–100 символів)
    - **author**: обов'язковий автор (3–50 символів)
    - **description**: необов'язковий опис (до 500 символів)
    - **year**: необов'язковий рік видання (1450 – поточний рік)
    - **rating**: необов'язкова оцінка (0.0 – 5.0, 1 десятковий знак)
    - **tags**: необов'язкові теги (список з дозволених значень)
    """
    book_id = str(uuid.uuid4())
    book_data = {"id": book_id, **book.model_dump()}
    books_db[book_id] = book_data
    return book_data


@app.get(
    "/books/",
    response_model=list[BookResponse],
    summary="Отримати всі книги",
    tags=["Книги"],
)
def get_books(
    author: Optional[str] = Query(None, description="Фільтр за автором (часткове збіг)"),
    year: Optional[int] = Query(None, description="Фільтр за роком видання"),
    tag: Optional[str] = Query(None, description="Фільтр за тегом"),
):
    """
    Повертає список всіх книг.

    Підтримує фільтрацію через query-параметри:
    - **author** – рядок, що міститься в імені автора (без урахування регістру)
    - **year** – точний рік видання
    - **tag** – тег, що входить до списку тегів книги
    """
    result = list(books_db.values())

    if author:
        result = [b for b in result if author.lower() in b["author"].lower()]
    if year is not None:
        result = [b for b in result if b.get("year") == year]
    if tag:
        result = [b for b in result if tag.lower() in (b.get("tags") or [])]

    return result


@app.get(
    "/books/{book_id}",
    response_model=BookResponse,
    summary="Отримати книгу за ID",
    tags=["Книги"],
)
def get_book(book_id: str):
    """Повертає одну книгу за її унікальним `id` або **404**, якщо не знайдена."""
    return get_book_or_404(book_id)


@app.put(
    "/books/{book_id}",
    response_model=BookResponse,
    summary="Оновити книгу",
    tags=["Книги"],
)
def update_book(book_id: str, update_data: BookUpdate):
    """
    Оновлює книгу за `id`.

    - Передавайте лише ті поля, що потрібно змінити.
    - Використовується `exclude_unset=True` — поля, яких немає в запиті, не змінюються.
    - Повертає **404**, якщо книгу не знайдено.
    """
    book = get_book_or_404(book_id)
    update_fields = update_data.model_dump(exclude_unset=True)
    book.update(update_fields)
    books_db[book_id] = book
    return book


@app.delete(
    "/books/{book_id}",
    summary="Видалити книгу",
    tags=["Книги"],
)
def delete_book(book_id: str):
    """
    Видаляє книгу за `id`.

    Повертає підтвердження або **404**, якщо книгу не знайдено.
    """
    book = get_book_or_404(book_id)
    del books_db[book_id]
    return {"message": f"Книгу «{book['title']}» успішно видалено"}


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "📚 Менеджер книжкової колекції",
        "docs": "/docs",
        "total_books": len(books_db),
    }