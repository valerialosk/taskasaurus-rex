# Taskasaurus Rex

Сервис планирования задач с поддержкой календаря, фильтрации и сортировки.

## Описание

RESTful API для управления задачами на FastAPI с функционалом:
- CRUD операции для задач и категорий
- Календарное представление (день, неделя, месяц)
- Фильтрация и сортировка задач
- Поддержка подзадач и просроченных задач

## Технологии

- FastAPI - веб-фреймворк
- SQLAlchemy - ORM
- PostgreSQL - база данных
- Pytest - тестирование
- Ruff, Black - линтинг и форматирование

## Структура проекта

```
app/
├── routes/         # API endpoints
├── models/         # SQLAlchemy модели
├── schemas/        # Pydantic схемы
├── services/       # Бизнес-логика
└── main.py         # Точка входа

tests/              # Тесты
.github/workflows/  # CI/CD
```

## Установка и запуск

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://localhost:8000/docs

## CI/CD

GitHub Actions автоматически проверяет:
- Линтинг (Ruff, Black)
- Build и компиляция
- Тесты (Pytest)
