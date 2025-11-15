"""
API endpoints для мониторинга производительности
"""
import logging
import time
from typing import Dict, Any
from fastapi import APIRouter
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Метрики производительности
performance_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0.0,
    "total_processing_time": 0.0,
    "cache_hits": 0,
    "cache_misses": 0,
}


@router.get("/performance", status_code=200)
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Получение метрик производительности
    
    Returns:
        Метрики производительности
    """
    avg_time = (
        performance_metrics["average_processing_time"]
        if performance_metrics["total_requests"] > 0
        else 0.0
    )
    
    cache_hit_rate = (
        performance_metrics["cache_hits"] / 
        (performance_metrics["cache_hits"] + performance_metrics["cache_misses"])
        if (performance_metrics["cache_hits"] + performance_metrics["cache_misses"]) > 0
        else 0.0
    )
    
    return {
        "total_requests": performance_metrics["total_requests"],
        "successful_requests": performance_metrics["successful_requests"],
        "failed_requests": performance_metrics["failed_requests"],
        "average_processing_time_seconds": round(avg_time, 3),
        "cache_hit_rate": round(cache_hit_rate * 100, 2),
        "cache_hits": performance_metrics["cache_hits"],
        "cache_misses": performance_metrics["cache_misses"],
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/performance/reset", status_code=200)
async def reset_performance_metrics():
    """Сброс метрик производительности"""
    global performance_metrics
    performance_metrics = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_processing_time": 0.0,
        "total_processing_time": 0.0,
        "cache_hits": 0,
        "cache_misses": 0,
    }
    return {"status": "success", "message": "Метрики сброшены"}


def update_metrics(
    processing_time: float,
    success: bool = True,
    cache_hit: bool = False
):
    """Обновление метрик производительности"""
    performance_metrics["total_requests"] += 1
    if success:
        performance_metrics["successful_requests"] += 1
    else:
        performance_metrics["failed_requests"] += 1
    
    if cache_hit:
        performance_metrics["cache_hits"] += 1
    else:
        performance_metrics["cache_misses"] += 1
    
    # Обновление среднего времени обработки
    total_time = performance_metrics["total_processing_time"] + processing_time
    total_requests = performance_metrics["total_requests"]
    performance_metrics["average_processing_time"] = total_time / total_requests
    performance_metrics["total_processing_time"] = total_time

