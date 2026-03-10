from fastapi import FastAPI
from typing import Optional

app = FastAPI()


# ─────────────────────────────────────────────
# Завдання 1. GET /hello
# Повертає {"message": "Hello, FastAPI!"}
# ─────────────────────────────────────────────
@app.get("/hello")
def hello():
    return {"message": "Hello, FastAPI!"}


# ─────────────────────────────────────────────
# Завдання 2. GET /square/{number}
# Path-параметр number (int) → піднести до квадрату
# ─────────────────────────────────────────────
@app.get("/square/{number}")
def square(number: int):
    return {"number": number, "square": number ** 2}


# ─────────────────────────────────────────────
# Завдання 3. GET /greet
# Query: name (str), age (int, необов'язково)
# ─────────────────────────────────────────────
@app.get("/greet")
def greet(name: str, age: Optional[int] = None):
    return {"message": f"Hello, {name}!", "age": age}


# ─────────────────────────────────────────────
# Завдання 4. GET /items/{item_id}
# Path: item_id (int), Query: q (str, необов'язково)
# ─────────────────────────────────────────────
@app.get("/items/{item_id}")
def get_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


# ─────────────────────────────────────────────
# Завдання 5. GET /calc
# Query: a (int), b (int)
# Повертає sum, diff, prod, div (або "undefined" якщо b=0)
# ─────────────────────────────────────────────
@app.get("/calc")
def calc(a: int, b: int):
    return {
        "a":    a,
        "b":    b,
        "sum":  a + b,
        "diff": a - b,
        "prod": a * b,
        "div":  a / b if b != 0 else "undefined",
    }