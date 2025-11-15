"""
API endpoints для обработки PDF
"""
import logging
import time
from io import BytesIO
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from ...config import settings
from ...models.schemas import PDFProcessResponse, ErrorResponse
from ...services.extractor import PaymentInvoiceExtractor
from ...utils.cache import pdf_cache
from .performance import update_metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/process-pdf",
    response_model=PDFProcessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Успешная обработка PDF"},
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        413: {"model": ErrorResponse, "description": "Файл слишком большой"},
        415: {"model": ErrorResponse, "description": "Неподдерживаемый тип файла"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    }
)
async def process_pdf(file: UploadFile = File(...)):
    """
    Обрабатывает PDF файл и извлекает структурированные данные
    
    Args:
        file: Загруженный PDF файл
        
    Returns:
        JSON с извлеченными данными
    """
    # Валидация типа файла
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Поддерживаются только PDF файлы"
        )
    
    # Чтение файла
    try:
        file_bytes = BytesIO(await file.read())
    except Exception as e:
        logger.error(f"Ошибка чтения файла: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при чтении файла"
        )
    
    # Проверка размера
    file_size = len(file_bytes.getvalue())
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_FILE_SIZE / (1024 * 1024):.0f} МБ"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл пустой"
        )
    
    start_time = time.time()
    
    # Проверка кэша
    file_hash = pdf_cache._generate_key(file_bytes.getvalue())
    cached_result = pdf_cache.get(file_hash)
    if cached_result:
        logger.info("Результат получен из кэша")
        processing_time = time.time() - start_time
        update_metrics(processing_time, success=True, cache_hit=True)
        return PDFProcessResponse(status="success", data=cached_result)
    
    # Обработка PDF
    try:
        extractor = PaymentInvoiceExtractor()
        
        # Сначала пробуем обычный парсинг, если не получается - используем OCR
        result = extractor.extract(file_bytes, use_ocr=False)
        
        # Если не удалось извлечь текст, пробуем OCR
        if not result or result.get("error"):
            logger.info("Обычный парсинг не дал результатов, пробую OCR...")
            file_bytes.seek(0)
            result = extractor.extract(file_bytes, use_ocr=True)
        
        # Замена None значений на спецслово
        result = _replace_none_with_unrecognized(result)
        
        # Сохранение в кэш
        pdf_cache.set(file_hash, result)
        
        processing_time = time.time() - start_time
        update_metrics(processing_time, success=True, cache_hit=False)
        
        return PDFProcessResponse(status="success", data=result)
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_metrics(processing_time, success=False, cache_hit=False)
        logger.error(f"Ошибка при обработке PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при обработке файла"
        )


def _replace_none_with_unrecognized(data: dict) -> dict:
    """
    Заменяет None значения на спецслово для нераспознанных полей
    
    Args:
        data: Словарь с данными
        
    Returns:
        Словарь с замененными значениями
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if value is None:
                result[key] = settings.UNRECOGNIZED_VALUE
            elif isinstance(value, dict):
                result[key] = _replace_none_with_unrecognized(value)
            elif isinstance(value, list):
                result[key] = [
                    _replace_none_with_unrecognized(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result
    return data

