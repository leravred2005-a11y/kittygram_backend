# Kittygram Backend

REST API для платформы Kittygram — сервиса публикации котиков с системой лайков и избранного.

## Стек технологий

- Python 3.11, Django 5.1, Django REST Framework 3.15
- Аутентификация: Token (djoser)
- Документация: drf-spectacular (Swagger / ReDoc)
- БД: SQLite (dev) / PostgreSQL (prod)

## Функциональность

- Регистрация и аутентификация пользователей
- CRUD котиков с фотографиями (Base64) и достижениями
- **Лайки**: поставить / убрать, список понравившихся, топ-10
- **Избранное**: добавить / убрать кота, список избранного
- Публичные эндпоинты: список котиков и топ-10 доступны без авторизации

## Как запустить локально

```bash
git clone https://github.com/leravred2005-a11y/kittygram_backend.git
cd kittygram_backend

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # при необходимости отредактировать

python manage.py migrate
python manage.py createsuperuser  # опционально

python manage.py runserver
```

## Запуск через Docker

```bash
cp .env.example .env   # заполнить SECRET_KEY и пароль БД

docker compose up --build
```

Приложение будет доступно на `http://localhost`.

## Переменные окружения (.env)

| Переменная       | Описание                  | По умолчанию |
|------------------|---------------------------|--------------|
| `SECRET_KEY`     | Секретный ключ Django      | insecure     |
| `DEBUG`          | Режим отладки             | True         |
| `ALLOWED_HOSTS`  | Разрешённые хосты         | *            |
| `POSTGRES_DB`    | Имя базы данных           | kittygram    |
| `POSTGRES_USER`  | Пользователь БД           | kittygram    |
| `POSTGRES_PASSWORD` | Пароль БД              | —            |

## API эндпоинты

### Аутентификация
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/users/` | Регистрация |
| POST | `/api/token/login/` | Получить токен |
| POST | `/api/token/logout/` | Удалить токен |

### Котики
| Метод | URL | Описание | Auth |
|-------|-----|----------|------|
| GET | `/api/cats/` | Список котиков | Нет |
| POST | `/api/cats/` | Создать котика | Да |
| GET | `/api/cats/{id}/` | Детали котика | Нет |
| PATCH | `/api/cats/{id}/` | Обновить (только владелец) | Да |
| DELETE | `/api/cats/{id}/` | Удалить (только владелец) | Да |
| GET | `/api/cats/top/` | Топ-10 по лайкам | Нет |

### Лайки
| Метод | URL | Описание | Auth |
|-------|-----|----------|------|
| POST | `/api/cats/{id}/like/` | Поставить лайк | Да |
| DELETE | `/api/cats/{id}/like/` | Убрать лайк | Да |
| GET | `/api/cats/liked/` | Котики, которым лайкнул | Да |

### Избранное
| Метод | URL | Описание | Auth |
|-------|-----|----------|------|
| POST | `/api/cats/{id}/favorite/` | Добавить в избранное | Да |
| DELETE | `/api/cats/{id}/favorite/` | Убрать из избранного | Да |
| GET | `/api/cats/favorites/` | Мои избранные | Да |

### Достижения
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/achievements/` | Список достижений |

### Документация
| URL | Описание |
|-----|----------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI schema (JSON) |

## Примеры запросов

### Регистрация и получение токена
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "valeria", "password": "Suslova2024!"}'

curl -X POST http://localhost:8000/api/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "valeria", "password": "Suslova2024!"}'
# → {"auth_token": "abc123..."}
```

### Создание котика
```bash
curl -X POST http://localhost:8000/api/cats/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{"name": "Мурзик", "color": "#FFA500", "birth_year": 2021}'
# → {"id": 1, "name": "Мурзик", "color": "orange", "likes_count": 0, ...}
```

### Лайк и избранное
```bash
# Лайк
curl -X POST http://localhost:8000/api/cats/1/like/ \
  -H "Authorization: Token abc123..."

# Добавить в избранное
curl -X POST http://localhost:8000/api/cats/1/favorite/ \
  -H "Authorization: Token abc123..."

# Мои избранные
curl http://localhost:8000/api/cats/favorites/ \
  -H "Authorization: Token abc123..."
```

### Топ котиков (без авторизации)
```bash
curl http://localhost:8000/api/cats/top/
```
