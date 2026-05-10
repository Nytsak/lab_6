# Library API — Лабораторна робота 6

REST API для керування бібліотекою книг із JWT-автентифікацією, побудований на **FastAPI** + **SQLAlchemy (async)**.

## Стек

| Компонент | Технологія |
|-----------|-----------|
| Фреймворк | FastAPI |
| База даних | SQLite (тести) / PostgreSQL (prod) через asyncpg |
| ORM | SQLAlchemy async |
| Автентифікація | PyJWT, bcrypt |
| Тести | pytest + pytest-asyncio |
| Запуск | Uvicorn, Docker |

## Швидкий старт

```bash
# 1. Встановити залежності
pip install -r requirements.txt

# 2. Скопіювати .env
cp .env.example .env   # задати SECRET_KEY та DATABASE_URL

# 3. Запустити
uvicorn main:app --reload --port 8080
```

Або через Docker:

```bash
docker-compose up --build
```

## API-ендпоінти

### Auth `/api/auth`

| Метод | Шлях | Опис |
|-------|------|------|
| POST | `/register` | Реєстрація користувача |
| POST | `/login` | Вхід, отримання токенів |
| POST | `/refresh` | Оновлення access-токена |
| POST | `/logout` | Інвалідація refresh-токена |

### Books `/api/books` *(потрібен Bearer token)*

| Метод | Шлях | Опис |
|-------|------|------|
| GET | `/books` | Список книг (пагінація, фільтри) |
| GET | `/books/{id}` | Деталі книги |
| POST | `/books` | Створити книгу |
| DELETE | `/books/{id}` | Видалити книгу |

## Тести

```bash
pytest tests/
```

Тести покривають реєстрацію, логін, CRUD книг та граничні випадки (конфлікт імені, невірний пароль тощо).

## Змінні середовища

| Змінна | За замовчуванням | Опис |
|--------|-----------------|------|
| `SECRET_KEY` | *(задати вручну)* | Ключ підпису JWT |
| `ALGORITHM` | `HS256` | Алгоритм JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Тривалість access-токена |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `3` | Тривалість refresh-токена |
| `DATABASE_URL` | SQLite | URL підключення до БД |