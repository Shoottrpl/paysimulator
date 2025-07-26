# REST API для управления пользователями и платежами

Асинхронное веб-приложение на Python с использованием Sanic и PostgreSQL, реализующее систему управления пользовательскими счетами и платежами с разделением ролей пользователя и администратора.

## 🔧 Технологический стек
- **Веб-фреймворк**: Sanic (асинхронный)
- **База данных**: PostgreSQL
- **ORM**: SQLAlchemy (асинхронная версия)
- **Контейнеризация**: Docker Compose
- **Аутентификация**: JWT-токены

## ⚙️ Основные функции
### Для пользователей
- Регистрация/авторизация
- Просмотр профиля
- Управление счетами
- Просмотр истории платежей

### Для администраторов
- Управление пользователями (CRUD)
- Просмотр всех счетов пользователей
- Обработка платежей через вебхуки

### Система платежей
- Верификация платежей через цифровые подписи
- Защита от повторного использования транзакций
- Автоматическое создание счетов

## 🚀 Быстрый запуск через Docker Compose

```bash
# 1. Клонировать репозиторий
git clone git@github.com:Shoottrpl/paysimulator.git
cd paysimulator

# 2. Запустить сервисы
docker-compose up --build -d

# 3. Применить миграции
make migrate

Сервисы будут доступны:

Приложение: http://localhost:8000

PostgreSQL: port 5432

```

## 🛠 Ручная установка (без Docker)

```bash
# 1. Установить зависимости
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Настройка окружения
cp .env.example .env
# Заполните параметры в .env

# 3. Запустить миграции
make migrate

# 4. Запустить приложение
python -m app.server
```
## 🔐 Тестовые учетные записи

**Пользователь**:  
📧 Email: `user@example.com`  
🔑 Пароль: `userpassword`

**Администратор**:  
📧 Email: `admin@example.com`  
🔑 Пароль: `adminpassword`

## 🌐Тестирование вебхука (эмуляция запроса)

Для проверки работы обработчика вебхука вы можете воспользоваться встроенным эмулятором:

```bash
python app/utils/webhook_emulator.py
```

**Что делает эмулятор:**
- Формирует тестовые данные транзакции
- Генерирует подпись
- Отправляет POST-запрос на эндпоинт `/api/webhook/transaction`
- Логирует результат (успех или ошибку)

**Важно:**  
Перед запуском убедитесь, что сервер приложения запущен и доступен по адресу `http://localhost:8000`.

## 🌐 Основные API-эндпоинты

| Метод  | Путь                  | Описание                     | Доступ     |
|--------|-----------------------|------------------------------|------------|
| POST   | `/auth/login`         | Авторизация                  | Все        |
| POST   | `/auth/logout`           | Выход из системы                | Пользователь|
| POST   | `/auth/refresh`          | Обновление токена               | Пользователь|
| GET    | `/users/me`           | Профиль текущего пользователя| Пользователь|
| GET    | `/accounts`           | Счета пользователя           | Пользователь|
| GET    | `/payments`           | Платежи пользователя         | Пользователь|
| POST   | `/admin/users`        | Создать пользователя         | Админ      |
| PUT    | `/admin/users/{id}`   | Обновить пользователя        | Админ      |
| DELETE | `/admin/users/{id}`   | Удалить пользователя         | Админ      |
| POST   | `/payment/webhook`    | Обработчик платежей          | Система    |

## 📁 Структура проекта
```text
├── app
│   ├── auth/              # Аутентификация и роли
│   ├── blueprints/        # API роуты (admin, auth, data, user, webhook)
│   ├── jwt/               # JWT-сервисы и схемы
│   ├── keys/              # Ключи (игнорируются в git, для структуры — .gitkeep)
│   ├── middleware/        # Мидлвейр (jwt_auth, session)
│   ├── schemas/           # Pydantic-схемы (account, auth, transaction, user, webhook, types)
│   ├── services/          # Сервисы (model_service)
│   ├── signature/         # Подписи (signature_service)
│   ├── utils/             # Вспомогательные функции (webhook_emulator)
│   ├── error_handling.py  # Обработка ошибок
│   ├── logger.py          # Логирование
│   ├── server.py          # Точка входа приложения
│   └── __init__.py
├── database
│   ├── models/            # SQLAlchemy-модели (account, token, transaction, user, base)
│   ├── engine.py          # Подключение к БД
│   └── __init__.py
├── migrations
│   ├── versions/          # Скрипты миграций Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── docker-compose.yml     # Конфигурация Docker Compose
├── Dockerfile             # Docker-образ приложения
├── requirements.txt       # Зависимости Python
├── makefile               # Make-команды для миграций и запуска
├── settings.py            # Настройки приложения
└── .gitignore             # Исключения для git
```
