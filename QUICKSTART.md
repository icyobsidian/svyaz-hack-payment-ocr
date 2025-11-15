# Быстрый старт

## Запуск через Docker Compose (рекомендуется)

### 1. Подготовка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd svyaz-hack-payment-ocr-1

# Создать .env файл
cp .env.example .env
```

### 2. Настройка Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен
5. Откройте файл `.env` и вставьте токен:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_здесь
   ```

### 3. Запуск

```bash
# Запустить все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 4. Проверка работы

- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### 5. Использование Telegram бота

1. Найдите вашего бота в Telegram (по username, который вы указали)
2. Отправьте `/start`
3. Отправьте PDF файл со сканом платежного счета
4. Получите структурированные данные в формате JSON

## Локальная разработка

### Backend

```bash
cd backend

# Установить зависимости
pip install -r requirements.txt

# Установить Tesseract OCR:
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
# macOS: brew install tesseract tesseract-lang

# Запустить сервер
uvicorn app.main:app --reload
```

### Telegram Bot

```bash
cd telegram_bot

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp env.example .env
# Заполнить TELEGRAM_BOT_TOKEN

# Запустить бота
python -m app.bot
```

## Тестирование API

### Через curl

```bash
curl -X POST "http://localhost:8000/api/v1/process-pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/invoice.pdf"
```

### Через Python

```python
import requests

url = "http://localhost:8000/api/v1/process-pdf"
files = {"file": open("invoice.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Структура ответа

Успешный ответ (200 OK):
```json
{
  "status": "success",
  "data": {
    "номер_счета": "12345",
    "дата": "01.01.2025",
    "плательщик": {
      "наименование": "ООО Пример",
      "ИНН": "1234567890"
    },
    "получатель": {...},
    "сумма": "10000.00",
    "назначение_платежа": "..."
  }
}
```

Ошибка (400/413/415/500):
```json
{
  "status": "error",
  "detail": "Описание ошибки",
  "error_code": 400
}
```

## Остановка сервисов

```bash
# Остановить все контейнеры
docker-compose down

# Остановить и удалить volumes
docker-compose down -v
```

## Логи

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f telegram-bot
```

## Устранение проблем

### Бот не отвечает

1. Проверьте, что токен правильный в `.env`
2. Проверьте логи: `docker-compose logs telegram-bot`
3. Убедитесь, что backend запущен: `docker-compose ps`

### Backend не запускается

1. Проверьте логи: `docker-compose logs backend`
2. Убедитесь, что порт 8000 свободен
3. Проверьте установку Tesseract OCR в контейнере

### OCR не работает

1. Убедитесь, что Tesseract установлен в системе
2. Проверьте языковые пакеты (rus, eng)
3. Проверьте настройки OCR_LANGUAGE в конфигурации

