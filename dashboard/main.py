from fastapi import FastAPI

from api.v1.endpoints import auth, dashboards, roles, stickers

app = FastAPI(
    title="Cockreate Boards & Stickers API",
    version="1.1.0",
    description=(
        "REST API для управления досками, стикерами и ролями пользователей. "
        "Все защищённые ручки используют JWT авторизацию."
    ),
)

app.include_router(auth.router)
app.include_router(dashboards.router)
app.include_router(roles.router)
app.include_router(stickers.router)


@app.get("/")
async def root():
    return {"message": "Cockreate API"}
