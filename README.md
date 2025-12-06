# Cockreate / Miro Clone

Многоуровневый сервис для совместной работы с досками и стикерами. Состоит из фронтенда, API для досок/стикеров и отдельного сервиса аутентификации.

## Структура репозитория
- `frontend/` — React + TypeScript + Vite клиент с авторизацией и экранами для работы с досками и карточками.
- `dashboard/` — FastAPI‑бэкенд для управления досками, стикерами и ролями участников.
- `AuthServer/` — ASP.NET Core API с JWT‑аутентификацией и SQL Server для хранения пользователей.
- `docker-compose.yml` — оркестрация всех сервисов и базы данных.

## Архитектура и основные функции
### Frontend (порт 80)
- SPA на React/Vite; роутинг `/signin`, `/signup`, `/reset-password`, `/` (список досок) и `/board/:id`.
- Использует защищённые маршруты и обращается к API через `VITE_API_URL` (по умолчанию `http://localhost:8080`).

### Dashboard API (порт 8080)
- FastAPI приложение с CORS, Swagger доступен на `/docs`.
- Авторизация через заголовок `Authorization: Bearer <token>`, проверка пользователей и ролей.
- Поддерживает CRUD досок, управление участниками (creator/editor/viewer) и работу со стикерами.
- Хранит данные в памяти (класс `State`), удобно для демонстрации и автотестов.

### Auth Server (порт 5001, база на 1433)
- ASP.NET Core Minimal API с JWT (секрет и издатель задаются через переменные окружения).
- Entity Framework Core + SQL Server для хранения пользователей; пароли в виде SHA-256 хэшей.
- Эндпоинты `/api/auth/register` и `/api/auth/login` для регистрации и выдачи токена на 24 часа.

## Запуск через Docker Compose
```bash
docker-compose up --build
```
Доступ после запуска:
- Фронтенд: http://localhost
- Dashboard API: http://localhost:8080 (Swagger: http://localhost:8080/docs)
- Auth Server: http://localhost:5001
- SQL Server: порт 1433 (volume `sqlserver-data`).

Переменные окружения:
- `VITE_API_URL` — адрес API для фронтенда (передаётся в билд Vite).
- `ConnectionStrings__DefaultConnection` и `JwtSettings__*` — конфигурация Auth Server (см. `docker-compose.yml`).

## Локальная разработка без Docker
- Frontend: `npm install && npm run dev` (см. `frontend/README.md`).
- Dashboard API: создать venv и установить зависимости `pip install -r requirements.txt`, запустить `uvicorn main:app --reload` (см. `dashboard/README.md`).
- Auth Server: `dotnet run` в `AuthServer/AuthServer/AuthServer` или использовать локальный docker-compose (см. `AuthServer/README.md`).
