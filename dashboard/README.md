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

## Запуск с Docker Compose

```bash
# Соберите и запустите сервис
docker compose up --build
```

Приложение будет доступно на http://localhost:8080 (Swagger UI: http://localhost:8080/docs).
