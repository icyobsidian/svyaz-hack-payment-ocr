# Telegram Bot для распознавания платежных счетов

Telegram-бот на aiogram для загрузки и обработки PDF файлов платежных счетов.

## Функциональность

- ✅ Загрузка PDF файлов через Telegram
- ✅ Валидация типа и размера файла
- ✅ Отправка файла на обработку в backend API
- ✅ Отображение результатов в читаемом формате
- ✅ Обработка всех типов ошибок (2xx, 3xx, 4xx, 5xx)

## Установка и запуск

### Локальная разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Заполните `TELEGRAM_BOT_TOKEN` (получить у @BotFather)

4. Запустите бота:
```bash
python -m app.bot
```

### Запуск через Docker

```bash
docker build -t telegram-bot .
docker run --env-file .env telegram-bot
```

## Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку

## Структура проекта

```
telegram_bot/
├── app/
│   ├── __init__.py
│   ├── bot.py          # Главный файл запуска
│   ├── config.py       # Конфигурация
│   ├── handlers.py     # Обработчики команд и сообщений
│   └── services.py     # Сервисы для работы с backend
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Интеграция с Backend

Бот отправляет POST запросы на endpoint:
```
POST {BACKEND_URL}/api/v1/process-pdf
Content-Type: multipart/form-data
Body: file (PDF файл)
```

Ожидаемый ответ при успехе (2xx, 3xx):
```json
{
  "status": "success",
  "data": {
    ...
  }
}
```

## Обработка ошибок

- **2xx/3xx**: JSON форматируется и отправляется пользователю
- **4xx**: Отправляется соответствующее сообщение об ошибке
- **5xx**: Отправляется общее сообщение об ошибке сервера

