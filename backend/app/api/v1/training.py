"""
API endpoints для обучения модели
"""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ...models.ml_model import FieldExtractionModel
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class TrainingExample(BaseModel):
    """Пример для обучения"""
    text: str
    expected_fields: Dict[str, Any]


class TrainingRequest(BaseModel):
    """Запрос на обучение модели"""
    examples: List[TrainingExample]


@router.post("/train-model", status_code=status.HTTP_200_OK)
async def train_model(request: TrainingRequest):
    """
    Обучение модели на предоставленных примерах
    
    Args:
        request: Запрос с примерами для обучения
        
    Returns:
        Статус обучения
    """
    if not request.examples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не предоставлены примеры для обучения"
        )
    
    try:
        model = FieldExtractionModel()
        
        # Подготовка данных
        training_data = [
            (example.text, example.expected_fields)
            for example in request.examples
        ]
        
        # Обучение
        model.train(training_data)
        
        return {
            "status": "success",
            "message": f"Модель обучена на {len(training_data)} примерах",
            "examples_count": len(training_data)
        }
        
    except Exception as e:
        logger.error(f"Ошибка при обучении модели: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обучении модели: {str(e)}"
        )

