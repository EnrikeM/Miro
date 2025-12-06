from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.endpoints import auth, dashboards, roles, stickers

app = FastAPI(
    title="Cockreate Boards & Stickers API",
    version="1.1.0",
    description=(
        "REST API для управления досками, стикерами и ролями пользователей. "
        "Все защищённые ручки используют JWT авторизацию."
    ),
)

# --- CORS ---
origins = [
    "http://localhost:3000",  
    "http://localhost:5173",  # фронтенд до билда
    "http://localhost:4173"   # фронтенд после билда
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,          
    allow_methods=["*"],             
    allow_headers=["*"],              
)

# --- ROUTERS ---
app.include_router(auth.router)
app.include_router(dashboards.router)
app.include_router(roles.router)
app.include_router(stickers.router)


@app.get("/")
async def root():
    return {"message": "Cockreate API"}
