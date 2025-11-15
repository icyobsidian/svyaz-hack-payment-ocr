# Сервис распознавания платежных счетов

Проект для Всероссийского хакатона связи 2025 от ООО «К ТЕЛЕКОМ»

## Описание

Сервис автоматического извлечения структурированных данных из платежных счетов в формате PDF через Telegram-бота.

## Функциональность

- 📄 Загрузка PDF-файлов через Telegram-бота
- 🔍 Автоматическое распознавание и извлечение данных из платежных счетов
- 📊 Возврат структурированных данных в формате JSON
- 🤖 Интеграция OCR для сканированных документов
- 🐳 Контейнеризация с Docker и Docker Compose
- 📓 Jupyter notebooks для демонстрации

## Структура проекта

```
svyaz-hack-payment-ocr-1/
├── backend/              # Backend API сервис
│   ├── app/
│   │   ├── main.py      # FastAPI приложение
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Pydantic схемы
│   │   ├── services/    # Бизнес-логика
│   │   └── utils/       # Утилиты (PDF парсинг, OCR)
│   ├── requirements.txt
│   └── Dockerfile
├── telegram_bot/        # Telegram бот
│   ├── app/
│   │   ├── bot.py
│   │   ├── handlers.py
│   │   └── services.py
│   ├── requirements.txt
│   └── Dockerfile
├── notebooks/           # Jupyter notebooks
│   └── pipeline_demo.ipynb
├── docker-compose.yml
├── .env.example
└── README.md
```

## Быстрый старт

📖 **Подробные инструкции:** См. [QUICKSTART.md](QUICKSTART.md)

### Предварительные требования

- Docker и Docker Compose
- Python 3.9+ (для локальной разработки)
- Telegram Bot Token (получить у @BotFather)

### Запуск через Docker Compose

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd svyaz-hack-payment-ocr-1
```

2. Создать `.env` файл:
```bash
cp .env.example .env
```

3. Заполнить `TELEGRAM_BOT_TOKEN` в `.env` (получить у @BotFather)

4. Запустить все сервисы:
```bash
docker-compose up --build
```

Сервисы будут доступны:
- Backend API: http://localhost:8000
- Telegram Bot: работает автоматически

### Локальная разработка

#### Backend

```bash
cd backend
pip install -r requirements.txt

# Установить Tesseract OCR
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
# macOS: brew install tesseract tesseract-lang

uvicorn app.main:app --reload
```

#### Telegram Bot

```bash
cd telegram_bot
pip install -r requirements.txt

# Создать .env файл с TELEGRAM_BOT_TOKEN
python -m app.bot
```

## API Endpoints

### POST /api/v1/process-pdf

Загрузка и обработка PDF-файла

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF файл

**Response:**
```json
{
  "status": "success",
  "data": {
    "номер_счета": "...",
    "дата": "...",
    "плательщик": {...},
    "получатель": {...},
    "сумма": "...",
    ...
  }
}
```

## Использование Telegram бота

1. Найдите бота в Telegram (по username, который вы указали при создании)
2. Отправьте команду `/start`
3. Отправьте PDF файл со сканом платежного счета
4. Получите структурированные данные в формате JSON

## Jupyter Notebooks

Для демонстрации работы пайплайна:

```bash
cd notebooks
jupyter notebook
```

Откройте `pipeline_demo.ipynb` для просмотра демонстрации.

## Конфигурация

Основные настройки в `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
BACKEND_URL=http://backend:8000
```

Дополнительные настройки в `backend/env.example` и `telegram_bot/env.example`.

## Технологии

- **Backend**: Python + FastAPI
- **Telegram Bot**: aiogram 3.x
- **PDF Processing**: PyMuPDF, pdfplumber
- **OCR**: Tesseract OCR
- **Контейнеризация**: Docker, Docker Compose

## Разработка

См. [ANALYSIS.md](ANALYSIS.md) для подробного анализа требований.

## Лицензия

Проект разработан для хакатона.
