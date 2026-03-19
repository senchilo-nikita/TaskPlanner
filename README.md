# Taskplanner

Веб-приложение для планирования задач на Django + PostgreSQL с адаптацией под смартфоны как PWA.

## Возможности

- регистрация, авторизация, подтверждение email;
- сброс пароля через email;
- список задач и kanban-доска;
- kanban-доска по статусам задач;
- приглашения в друзья по email;
- создание задач для себя и подтвержденных друзей;
- PWA-манифест и service worker.

## Запуск

1. Скопируйте `.env.example` в `.env`.
2. Запустите:

```bash
docker compose up --build
```

3. Приложение будет доступно по адресу [http://localhost:8000](http://localhost:8000).
4. Почтовые письма для локальной разработки доступны в Mailpit: [http://localhost:8025](http://localhost:8025).

## Тестовый аккаунт

- email: `demo@taskplanner.local`
- пароль: `DemoPass123!`
- email: `friend@taskplanner.local`
- пароль: `FriendPass123!`

Пользователи создаются автоматически при выполнении миграций.

## Основные переменные окружения

- `SECRET_KEY`
- `DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `DEFAULT_FROM_EMAIL`
