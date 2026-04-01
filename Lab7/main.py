from fastapi import FastAPI
from database import engine, Base
from routers import users, events, departments, roles

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🚀 Space Station Event Manager",
    description=(
        "Система управління подіями на космічній станції. "
        "Відділи: Scientific, Technical, Medical. "
        "Ролі: Crew, Commander, Scientist."
    ),
    version="1.0.0",
)

app.include_router(roles.router)
app.include_router(departments.router)
app.include_router(users.router)
app.include_router(events.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "mission": "Space Station Event Manager",
        "docs": "/docs",
    }
