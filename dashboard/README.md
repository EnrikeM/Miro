```bash
# Создание виртуального окружения
python -m venv venv
```
```bash
# активация окружения Windows
venv\Scripts\activate
```

```bash
# Linux/Mac
source venv/bin/activate
```

```bash
# Установите зависимости
pip install -r requirements.txt
```

## Запуск с Docker Compose (PostgreSQL)

```bash
# Создайте файл окружения с DSN до postgres контейнера
cp .env.example .env

# Соберите и запустите сервис + базу
docker compose up --build
```

В процессе старта выполняются Alembic миграции (`alembic upgrade head`).

Доступ к API: http://localhost:8080 (Swagger UI: http://localhost:8080/docs).
