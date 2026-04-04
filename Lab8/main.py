from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import bookings, rooms, users

app = FastAPI(
    title="Система розумного бронювання переговорних кімнат",
    description="""
## Архітектура
- **BookingService** / **RoomService** — вся бізнес-логіка
- **BookingRepository** / **RoomRepository** / **UserRepository** — лише доступ до даних
- Dependency Injection через FastAPI `Depends`

## Бізнес-правила
| Правило | Employee | Manager |
|---|---|---|
| Макс. активних бронювань | 2 | необмежено |
| Макс. тривалість | 2 год | необмежено |
| Конфлікт з employee | ❌ заборонено | ✅ витісняє |
| Конфлікт з manager | ❌ заборонено | ❌ заборонено |
| Неактивна кімната | ❌ | ❌ |
""",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router)
app.include_router(rooms.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Smart Room Booking"}
