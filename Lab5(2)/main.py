from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Book Collection Manager")

_books: dict[int, dict] = {}
_next_id = 1

CURRENT_YEAR = datetime.now().year
VALID_TAGS = {"класика", "фантастика", "навчальна", "детектив",
              "біографія", "наукова", "пригоди", "роман", "поезія"}


class BookCreate(BaseModel):
    title:       str             = Field(min_length=3, max_length=100)
    author:      str             = Field(min_length=3, max_length=50)
    description: Optional[str]  = Field(default=None, max_length=500)
    year:        Optional[int]  = Field(default=None, ge=1450, le=CURRENT_YEAR)
    rating:      Optional[float]= Field(default=None, ge=0.0, le=5.0)
    tags:        Optional[list[str]] = Field(default=None)

    @field_validator("rating")
    @classmethod
    def check_rating_precision(cls, v):
        if v is not None and round(v, 1) != v:
            raise ValueError("rating повинен мати максимум 1 десятковий знак")
        return v

    @field_validator("tags")
    @classmethod
    def check_tags(cls, v):
        if v is not None:
            invalid = [t for t in v if t not in VALID_TAGS]
            if invalid:
                raise ValueError(f"Невідомі теги: {invalid}. Допустимі: {sorted(VALID_TAGS)}")
        return v


class BookUpdate(BaseModel):
    title:       Optional[str]       = Field(default=None, min_length=3, max_length=100)
    author:      Optional[str]       = Field(default=None, min_length=3, max_length=50)
    description: Optional[str]       = Field(default=None, max_length=500)
    year:        Optional[int]       = Field(default=None, ge=1450, le=CURRENT_YEAR)
    rating:      Optional[float]     = Field(default=None, ge=0.0, le=5.0)
    tags:        Optional[list[str]] = Field(default=None)

    @field_validator("rating")
    @classmethod
    def check_rating_precision(cls, v):
        if v is not None and round(v, 1) != v:
            raise ValueError("rating повинен мати максимум 1 десятковий знак")
        return v

    @field_validator("tags")
    @classmethod
    def check_tags(cls, v):
        if v is not None:
            invalid = [t for t in v if t not in VALID_TAGS]
            if invalid:
                raise ValueError(f"Невідомі теги: {invalid}. Допустимі: {sorted(VALID_TAGS)}")
        return v


class BookResponse(BaseModel):
    id:          int
    title:       str
    author:      str
    description: Optional[str]
    year:        Optional[int]
    rating:      Optional[float]
    tags:        Optional[list[str]]


def _get_or_404(book_id: int) -> dict:
    book = _books.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Книгу з id={book_id} не знайдено")
    return book


@app.post("/books/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    global _next_id
    new_book = {"id": _next_id, **book.model_dump()}
    _books[_next_id] = new_book
    _next_id += 1
    return new_book


@app.get("/books/", response_model=list[BookResponse])
def get_books(
    author: Optional[str] = Query(default=None, description="Фільтр по автору"),
    year:   Optional[int] = Query(default=None, description="Фільтр по року"),
    tag:    Optional[str] = Query(default=None, description="Фільтр по тегу"),
):
    result = list(_books.values())
    if author:
        result = [b for b in result if author.lower() in b["author"].lower()]
    if year:
        result = [b for b in result if b["year"] == year]
    if tag:
        result = [b for b in result if b["tags"] and tag in b["tags"]]
    return result


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    return _get_or_404(book_id)


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updates: BookUpdate):
    book = _get_or_404(book_id)
    book.update(updates.model_dump(exclude_unset=True))
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = _get_or_404(book_id)
    _books.pop(book_id)
    return {"message": f"Книгу «{book['title']}» успішно видалено"}