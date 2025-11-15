"""
Pydantic схемы для валидации данных
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class PDFProcessResponse(BaseModel):
    """Схема ответа при успешной обработке PDF"""
    status: str = "success"
    data: Dict[str, Any] = Field(..., description="Структурированные данные из PDF")


class ErrorResponse(BaseModel):
    """Схема ответа при ошибке"""
    status: str = "error"
    detail: str = Field(..., description="Описание ошибки")
    error_code: Optional[int] = None


class FieldExtractionResult(BaseModel):
    """Результат извлечения одного поля"""
    field_name: str
    value: Any
    confidence: Optional[float] = None


class PaymentInvoiceData(BaseModel):
    """Структура данных платежного счета"""
    # Основная информация
    номер_счета: Optional[str] = None
    дата: Optional[str] = None
    
    # Плательщик
    плательщик: Optional[Dict[str, Any]] = None
    
    # Получатель
    получатель: Optional[Dict[str, Any]] = None
    
    # Финансовая информация
    сумма: Optional[str] = None
    сумма_прописью: Optional[str] = None
    
    # Назначение платежа
    назначение_платежа: Optional[str] = None
    
    # Банковские реквизиты
    банк_плательщика: Optional[Dict[str, Any]] = None
    банк_получателя: Optional[Dict[str, Any]] = None
    
    # Дополнительные поля
    дополнительные_поля: Optional[Dict[str, Any]] = None
    
    # Новые поля
    валюта: Optional[str] = None
    НДС: Optional[str] = None
    сумма_прописью: Optional[str] = None
    договор: Optional[str] = None
    срок_оплаты: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "номер_счета": "12345",
                "дата": "01.01.2025",
                "плательщик": {
                    "наименование": "ООО Пример",
                    "ИНН": "1234567890",
                    "КПП": "123456789"
                },
                "получатель": {
                    "наименование": "ООО Получатель",
                    "ИНН": "0987654321"
                },
                "сумма": "10000.00",
                "назначение_платежа": "Оплата по договору"
            }
        }

