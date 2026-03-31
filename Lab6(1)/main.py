import asyncio
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Lab 6")


# ──────────────────────────────────────────────
# Завдання 1
# ──────────────────────────────────────────────

class Address(BaseModel):
    city: str
    street: str


class UserCreate(BaseModel):
    name: str
    address: Address


@app.post("/users", response_model=UserCreate)
async def create_user(user: UserCreate) -> UserCreate:
    """
    Приймає вкладену модель UserCreate (з Address всередині)
    та повертає отримані дані без змін.
    """
    return user


# ──────────────────────────────────────────────
# Завдання 2
# ──────────────────────────────────────────────

class Item(BaseModel):
    name: str
    price: float


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """
    Імітує повільну асинхронну операцію (наприклад, запит до БД).

    Що відбувається з event loop під час await asyncio.sleep(2):
    - Корутина призупиняється і повертає керування event loop-у.
    - Event loop може в цей час обробляти інші запити або задачі.
    - Через 2 секунди корутина відновлюється з того самого місця.
    - Це НЕ блокує весь сервер — інші клієнти отримують відповіді
      паралельно, на відміну від блокуючого time.sleep().
    """
    await asyncio.sleep(2)
    return Item(name=f"Item #{item_id}", price=round(item_id * 9.99, 2))


# ──────────────────────────────────────────────
# Завдання 3
# ──────────────────────────────────────────────

class Product(BaseModel):
    title: str
    price: float


class Order(BaseModel):
    order_id: int
    products: list[Product]
    total: float = 0.0


async def fetch_products_group_a(order_id: int) -> list[Product]:
    """Імітує отримання першої групи продуктів з затримкою."""
    await asyncio.sleep(1)
    return [
        Product(title=f"Product A1 (order {order_id})", price=100.0),
        Product(title=f"Product A2 (order {order_id})", price=250.5),
    ]


async def fetch_products_group_b(order_id: int) -> list[Product]:
    """Імітує отримання другої групи продуктів з затримкою."""
    await asyncio.sleep(1)
    return [
        Product(title=f"Product B1 (order {order_id})", price=75.0),
        Product(title=f"Product B2 (order {order_id})", price=49.99),
    ]


@app.get("/order/{order_id}", response_model=Order)
async def get_order(order_id: int) -> Order:
    """
    asyncio.gather запускає обидві корутини ОДНОЧАСНО.
    Загальний час очікування ≈ 1 с (а не 1+1=2 с),
    бо обидві йдуть паралельно в рамках одного event loop-у.
    """
    group_a, group_b = await asyncio.gather(
        fetch_products_group_a(order_id),
        fetch_products_group_b(order_id),
    )

    all_products: list[Product] = group_a + group_b
    total = round(sum(p.price for p in all_products), 2)

    return Order(order_id=order_id, products=all_products, total=total)


# ──────────────────────────────────────────────
# Завдання 4
# ──────────────────────────────────────────────

class Profile(BaseModel):
    bio: str
    age: int


class User(BaseModel):
    username: str
    profile: Optional[Profile] = None


class ProfileCheckResponse(BaseModel):
    username: str
    has_profile: bool
    message: str
    profile: Optional[Profile] = None


@app.post("/profile-check", response_model=ProfileCheckResponse)
async def profile_check(user: User) -> ProfileCheckResponse:
    """
    Асинхронна затримка виконується ЛИШЕ якщо профіль передано.
    Якщо profile=None — відповідь повертається миттєво.
    """
    if user.profile is not None:
        await asyncio.sleep(1)
        return ProfileCheckResponse(
            username=user.username,
            has_profile=True,
            message="Профіль знайдено та перевірено.",
            profile=user.profile,
        )

    return ProfileCheckResponse(
        username=user.username,
        has_profile=False,
        message="Профіль відсутній. Асинхронна перевірка пропущена.",
    )