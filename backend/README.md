# Backend API для распознавания платежных счетов

FastAPI сервис для обработки PDF файлов и извлечения структурированных данных из платежных счетов.

## Функциональность

- ✅ Загрузка и валидация PDF файлов
- ✅ Извлечение текста из PDF (PyMuPDF, pdfplumber)
- ✅ OCR для сканированных документов (Tesseract)
- ✅ Извлечение структурированных данных (регулярные выражения)
- ✅ Возврат данных в формате JSON
- ✅ Обработка ошибок с правильными HTTP статусами

## Установка и запуск

### Локальная разработка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Установите Tesseract OCR:
   - **Windows**: Скачайте с [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng`
   - **macOS**: `brew install tesseract tesseract-lang`

3. Создайте файл `.env` (опционально):
```bash
cp env.example .env
```

4. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

API будет доступен по адресу: http://localhost:8000

### Запуск через Docker

```bash
docker build -t backend-api .
docker run -p 8000:8000 backend-api
```

## API Endpoints

### POST /api/v1/process-pdf

Обработка PDF файла и извлечение данных.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF файл

**Response (200 OK):**
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

**Ошибки:**
- `400` - Неверный формат запроса
- `413` - Файл слишком большой
- `415` - Неподдерживаемый тип файла
- `500` - Внутренняя ошибка сервера

### GET /health

Health check endpoint.

### GET /

Информация о сервисе.

## Структура проекта

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация
│   ├── api/
│   │   └── v1/
│   │       └── endpoints.py # API endpoints
│   ├── models/
│   │   └── schemas.py       # Pydantic схемы
│   ├── services/
│   │   └── extractor.py     # Извлечение данных
│   └── utils/
│       ├── pdf_parser.py    # Парсинг PDF
│       └── ocr.py           # OCR обработка
├── requirements.txt
├── Dockerfile
├── env.example
└── README.md
```

## Извлекаемые поля

- Номер счета
- Дата
- Плательщик (наименование, ИНН, КПП)
- Получатель (наименование, ИНН, КПП)
- Сумма
- Назначение платежа
- Банковские реквизиты (БИК, р/с, наименование банка)

## Технологии

- **FastAPI** - современный веб-фреймворк
- **PyMuPDF / pdfplumber** - парсинг PDF
- **Tesseract OCR** - распознавание текста
- **Pydantic** - валидация данных
- **Regex** - извлечение структурированных данных

## Улучшения

Для повышения точности можно:
- Использовать ML модели для извлечения полей
- Fine-tuning моделей на датасете платежных счетов
- Использовать специализированные библиотеки (docTR, LayoutLM)
- Улучшить регулярные выражения на основе реальных данных

