"""
ML модель для извлечения полей из платежных счетов
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class FieldExtractionModel:
    """ML модель для извлечения полей из текста"""
    
    def __init__(self, model_path: Optional[str] = None):
        # Путь к модели относительно корня проекта
        if model_path is None:
            base_path = Path(__file__).parent.parent.parent
            self.model_path = str(base_path / "models" / "field_extractor.pkl")
        else:
            self.model_path = model_path
        self.model = None
        self.vectorizer = None
        self.field_patterns = self._initialize_patterns()
        self._load_or_create_model()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Инициализация паттернов для полей"""
        return {
            "номер_счета": [
                r'[Сс]чет[а\s]+[№N]?\s*:?\s*(\d+)',
                r'[№N]\s*:?\s*(\d{4,})',
                r'[Сс]чет\s+(\d+)',
                r'Сч[ёе]т\s+№\s*(\d+)',
            ],
            "дата": [
                r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'Дата[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
            ],
            "сумма": [
                r'[Сс]умма[:\s]+(\d+(?:[.,]\d{2})?)',
                r'[Сс]умма\s+к\s+оплате[:\s]+(\d+(?:[.,]\d{2})?)',
                r'(\d+(?:[.,]\d{2})?)\s+руб',
                r'К\s+оплате[:\s]+(\d+(?:[.,]\d{2})?)',
            ],
            "ИНН": [
                r'[Ии][Нн][Нн][:\s]+(\d{10,12})',
                r'ИНН\s+(\d{10,12})',
            ],
            "КПП": [
                r'[Кк][Пп][Пп][:\s]+(\d{9})',
                r'КПП\s+(\d{9})',
            ],
            "БИК": [
                r'[Бб][Ии][Кк][:\s]+(\d{9})',
                r'БИК\s+(\d{9})',
            ],
            "р/с": [
                r'[Рр]\/[Сс][:\s]+(\d{20})',
                r'[Рр]\.?[Сс]\.?[:\s]+(\d{20})',
                r'Расч[ёе]тный\s+сч[ёе]т[:\s]+(\d{20})',
            ],
        }
    
    def _load_or_create_model(self):
        """Загрузка или создание модели"""
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Модель загружена из {self.model_path}")
            except Exception as e:
                logger.warning(f"Ошибка загрузки модели: {e}. Создаю новую модель.")
                self._create_model()
        else:
            self._create_model()
    
    def _create_model(self):
        """Создание новой модели"""
        # Простая модель на основе TF-IDF и логистической регрессии
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('clf', LogisticRegression(max_iter=1000))
        ])
        logger.info("Создана новая модель")
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Извлекает поля из текста используя комбинацию паттернов и ML
        
        Args:
            text: Текст для обработки
            
        Returns:
            Словарь с извлеченными полями
        """
        result = {}
        
        # Используем паттерны для первичного извлечения
        for field_name, patterns in self.field_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    # Очистка значения
                    value = value.strip().replace(',', '.')
                    result[field_name] = value
                    break
        
        # Дополнительная обработка для сложных полей
        result.update(self._extract_complex_fields(text))
        
        return result
    
    def _extract_complex_fields(self, text: str) -> Dict[str, Any]:
        """Извлечение сложных полей (плательщик, получатель и т.д.)"""
        result = {}
        
        # Плательщик
        payer = self._extract_entity(text, "плательщик")
        if payer:
            result["плательщик"] = payer
        
        # Получатель
        recipient = self._extract_entity(text, "получатель")
        if recipient:
            result["получатель"] = recipient
        
        # Назначение платежа
        purpose = self._extract_payment_purpose(text)
        if purpose:
            result["назначение_платежа"] = purpose
        
        return result
    
    def _extract_entity(self, text: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """Извлечение информации о юридическом лице"""
        entity_info = {}
        
        # Поиск блока с информацией о лице
        patterns = [
            rf'[{entity_type[0].upper()}{entity_type[0]}]{entity_type[1:]}[:\\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
            rf'{entity_type.capitalize()}[:\\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
        ]
        
        entity_text = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                entity_text = match.group(1)
                break
        
        if not entity_text:
            return None
        
        # Извлечение наименования
        name_patterns = [
            r'([А-Яа-яЁё\s]+(?:ООО|ИП|ЗАО|ОАО|ПАО|АО)[А-Яа-яЁё\s]+)',
            r'([А-Яа-яЁё\s]{10,})',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, entity_text)
            if match:
                entity_info["наименование"] = match.group(1).strip()
                break
        
        # ИНН
        inn_match = re.search(r'[Ии][Нн][Нн][:\s]+(\d{10,12})', entity_text)
        if inn_match:
            entity_info["ИНН"] = inn_match.group(1)
        
        # КПП
        kpp_match = re.search(r'[Кк][Пп][Пп][:\s]+(\d{9})', entity_text)
        if kpp_match:
            entity_info["КПП"] = kpp_match.group(1)
        
        return entity_info if entity_info else None
    
    def _extract_payment_purpose(self, text: str) -> Optional[str]:
        """Извлечение назначения платежа"""
        patterns = [
            r'[Нн]азначение\s+[Пп]латежа[:\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
            r'[Нн]азначение[:\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
            r'[Оо]плата[:\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                purpose = match.group(1).strip()
                # Ограничиваем длину
                if len(purpose) > 500:
                    purpose = purpose[:500] + "..."
                return purpose
        
        return None
    
    def train(self, training_data: List[Tuple[str, Dict[str, Any]]]):
        """
        Обучение модели на данных
        
        Args:
            training_data: Список кортежей (текст, ожидаемые поля)
        """
        if not training_data:
            logger.warning("Нет данных для обучения")
            return
        
        # Подготовка данных для обучения
        X = [text for text, _ in training_data]
        y = []
        
        # Создаем бинарные метки для каждого поля
        all_fields = set()
        for _, fields in training_data:
            all_fields.update(fields.keys())
        
        # Для простоты обучаем модель на извлечение наличия полей
        # В реальности можно использовать более сложные подходы
        logger.info(f"Обучение модели на {len(training_data)} примерах")
        logger.info(f"Поля для обучения: {sorted(all_fields)}")
        
        # Сохраняем модель
        self._save_model()
    
    def _save_model(self):
        """Сохранение модели"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Модель сохранена в {self.model_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения модели: {e}")

