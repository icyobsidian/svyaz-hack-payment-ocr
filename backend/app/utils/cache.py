"""
Кэширование для оптимизации производительности
"""
import hashlib
import logging
from typing import Optional, Any
from functools import lru_cache
import json

logger = logging.getLogger(__name__)


class SimpleCache:
    """Простой in-memory кэш"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def _generate_key(self, data: Any) -> str:
        """Генерация ключа кэша"""
        if isinstance(data, bytes):
            return hashlib.md5(data).hexdigest()
        elif isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        else:
            return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        if key in self.cache:
            # Обновляем порядок доступа
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Сохранение значения в кэш"""
        # Удаляем старые записи, если кэш переполнен
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = value
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self):
        """Очистка кэша"""
        self.cache.clear()
        self.access_order.clear()


# Глобальный экземпляр кэша
pdf_cache = SimpleCache(max_size=50)

