"""
Сервис для извлечения структурированных данных из платежных счетов
"""
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import settings
from ..utils.pdf_parser import PDFParser
from ..utils.ocr import OCRProcessor
from ..models.ml_model import FieldExtractionModel

logger = logging.getLogger(__name__)


class PaymentInvoiceExtractor:
    """Извлекатель данных из платежных счетов"""
    
    def __init__(self, use_ml: bool = True):
        self.pdf_parser = PDFParser()
        self.ocr_processor = None
        self.ml_model = None
        
        try:
            self.ocr_processor = OCRProcessor()
        except ImportError:
            logger.warning("OCR недоступен, будет использоваться только текстовый парсинг")
        
        if use_ml:
            try:
                self.ml_model = FieldExtractionModel()
                logger.info("ML модель инициализирована")
            except Exception as e:
                logger.warning(f"ML модель недоступна: {e}. Используется только regex.")
    
    def extract(self, pdf_bytes, use_ocr: bool = False) -> Dict[str, Any]:
        """
        Извлекает структурированные данные из PDF
        
        Args:
            pdf_bytes: Байты PDF файла
            use_ocr: Использовать ли OCR для сканированных документов
            
        Returns:
            Словарь с извлеченными данными
        """
        # Извлечение текста
        if use_ocr and self.ocr_processor:
            text = self.ocr_processor.extract_text_from_pdf_images(pdf_bytes)
        else:
            try:
                text = self.pdf_parser.extract_text(pdf_bytes)
            except Exception as e:
                logger.error(f"Ошибка парсинга PDF: {e}")
                if self.ocr_processor:
                    logger.info("Пробую использовать OCR...")
                    text = self.ocr_processor.extract_text_from_pdf_images(pdf_bytes)
                else:
                    text = ""
        
        if not text.strip():
            return {"error": "Не удалось извлечь текст из PDF"}
        
        # Извлечение структурированных данных
        if self.ml_model:
            # Используем ML модель для извлечения
            ml_result = self.ml_model.extract_fields(text)
            # Дополняем результатами regex парсинга
            regex_result = self._parse_text(text)
            result = self._merge_results(ml_result, regex_result)
        else:
            # Используем только regex
            result = self._parse_text(text)
        
        return result
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """
        Парсит текст и извлекает структурированные данные
        
        Args:
            text: Извлеченный текст
            
        Returns:
            Словарь с извлеченными данными
        """
        result = {}
        
        # Номер счета
        account_number = self._extract_account_number(text)
        if account_number:
            result["номер_счета"] = account_number
        
        # Дата
        date = self._extract_date(text)
        if date:
            result["дата"] = date
        
        # Плательщик
        payer = self._extract_payer(text)
        if payer:
            result["плательщик"] = payer
        
        # Получатель
        recipient = self._extract_recipient(text)
        if recipient:
            result["получатель"] = recipient
        
        # Сумма
        amount = self._extract_amount(text)
        if amount:
            result["сумма"] = amount
        
        # Назначение платежа
        purpose = self._extract_payment_purpose(text)
        if purpose:
            result["назначение_платежа"] = purpose
        
        # Банковские реквизиты
        bank_info = self._extract_bank_info(text)
        if bank_info:
            if bank_info.get("плательщик"):
                result["банк_плательщика"] = bank_info["плательщик"]
            if bank_info.get("получатель"):
                result["банк_получателя"] = bank_info["получатель"]
        
        # Дополнительные поля
        additional = self._extract_additional_fields(text)
        if additional:
            result["дополнительные_поля"] = additional
        
        return result
    
    def _extract_account_number(self, text: str) -> Optional[str]:
        """Извлекает номер счета"""
        patterns = [
            r'[Сс]чет[а\s]+[№N]?\s*:?\s*(\d+)',
            r'[№N]\s*:?\s*(\d{4,})',
            r'[Сс]чет\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Извлекает дату"""
        patterns = [
            r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Берем первую найденную дату
                return matches[0]
        
        return None
    
    def _extract_payer(self, text: str) -> Optional[Dict[str, Any]]:
        """Извлекает информацию о плательщике"""
        payer_info = {}
        
        # Наименование плательщика
        patterns_name = [
            r'[Пп]лательщик[:\s]+([А-Яа-яЁё\s]+(?:ООО|ИП|ЗАО|ОАО)[А-Яа-яЁё\s]+)',
            r'[Пп]лательщик[:\s]+(.+?)(?:\n|ИНН|КПП)',
        ]
        
        for pattern in patterns_name:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                payer_info["наименование"] = match.group(1).strip()
                break
        
        # ИНН плательщика
        inn_match = re.search(r'[Ии][Нн][Нн][:\s]+(\d{10,12})', text)
        if inn_match:
            payer_info["ИНН"] = inn_match.group(1)
        
        # КПП плательщика
        kpp_match = re.search(r'[Кк][Пп][Пп][:\s]+(\d{9})', text)
        if kpp_match:
            payer_info["КПП"] = kpp_match.group(1)
        
        return payer_info if payer_info else None
    
    def _extract_recipient(self, text: str) -> Optional[Dict[str, Any]]:
        """Извлекает информацию о получателе"""
        recipient_info = {}
        
        # Наименование получателя
        patterns_name = [
            r'[Пп]олучатель[:\s]+([А-Яа-яЁё\s]+(?:ООО|ИП|ЗАО|ОАО)[А-Яа-яЁё\s]+)',
            r'[Пп]олучатель[:\s]+(.+?)(?:\n|ИНН|КПП)',
        ]
        
        for pattern in patterns_name:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                recipient_info["наименование"] = match.group(1).strip()
                break
        
        # ИНН получателя
        inn_match = re.search(r'[Ии][Нн][Нн][:\s]+(\d{10,12})', text)
        if inn_match:
            recipient_info["ИНН"] = inn_match.group(1)
        
        # КПП получателя
        kpp_match = re.search(r'[Кк][Пп][Пп][:\s]+(\d{9})', text)
        if kpp_match:
            recipient_info["КПП"] = kpp_match.group(1)
        
        return recipient_info if recipient_info else None
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """Извлекает сумму"""
        patterns = [
            r'[Сс]умма[:\s]+(\d+(?:[.,]\d{2})?)',
            r'[Сс]умма\s+к\s+оплате[:\s]+(\d+(?:[.,]\d{2})?)',
            r'(\d+(?:[.,]\d{2})?)\s+руб',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).replace(',', '.')
        
        return None
    
    def _extract_payment_purpose(self, text: str) -> Optional[str]:
        """Извлекает назначение платежа"""
        patterns = [
            r'[Нн]азначение\s+[Пп]латежа[:\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
            r'[Нн]азначение[:\s]+(.+?)(?:\n\n|\n[А-Я]|$)',
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
    
    def _extract_bank_info(self, text: str) -> Dict[str, Any]:
        """Извлекает банковские реквизиты"""
        bank_info = {}
        
        # БИК
        bik_pattern = r'[Бб][Ии][Кк][:\s]+(\d{9})'
        bik_match = re.search(bik_pattern, text)
        
        # Расчетный счет
        account_pattern = r'[Рр]\/[Сс][:\s]+(\d{20})'
        account_match = re.search(account_pattern, text)
        
        # Наименование банка
        bank_name_pattern = r'[Бб]анк[:\s]+(.+?)(?:\n|БИК|ИНН)'
        bank_name_match = re.search(bank_name_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if bik_match or account_match or bank_name_match:
            bank_data = {}
            if bik_match:
                bank_data["БИК"] = bik_match.group(1)
            if account_match:
                bank_data["р/с"] = account_match.group(1)
            if bank_name_match:
                bank_data["наименование"] = bank_name_match.group(1).strip()
            
            # Пытаемся определить, к кому относится (плательщик или получатель)
            # Это упрощенная логика, можно улучшить
            bank_info["получатель"] = bank_data
        
        return bank_info
    
    def _extract_additional_fields(self, text: str) -> Dict[str, Any]:
        """Извлекает дополнительные поля"""
        additional = {}
        
        # Валюта
        currency_match = re.search(r'[Вв]алюта[:\s]+([А-Яа-яЁёA-Za-z]{3})', text, re.IGNORECASE)
        if currency_match:
            additional["валюта"] = currency_match.group(1).upper()
        
        # НДС
        vat_patterns = [
            r'[Нн][Дд][Сс][:\s]+(\d+(?:[.,]\d{2})?)',
            r'[Нн]ДС[:\s]+(\d+(?:[.,]\d{2})?)',
            r'[Вв]ключая\s+НДС[:\s]+(\d+(?:[.,]\d{2})?)',
        ]
        for pattern in vat_patterns:
            vat_match = re.search(pattern, text, re.IGNORECASE)
            if vat_match:
                additional["НДС"] = vat_match.group(1).replace(',', '.')
                break
        
        # Сумма прописью
        amount_words_pattern = r'[Сс]умма\s+прописью[:\s]+(.+?)(?:\n|Сумма|Итого)'
        amount_words_match = re.search(amount_words_pattern, text, re.IGNORECASE | re.DOTALL)
        if amount_words_match:
            additional["сумма_прописью"] = amount_words_match.group(1).strip()[:200]
        
        # Договор/соглашение
        contract_patterns = [
            r'[Дд]оговор[:\s]+(.+?)(?:\n|от|№)',
            r'[Сс]оглашение[:\s]+(.+?)(?:\n|от|№)',
        ]
        for pattern in contract_patterns:
            contract_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if contract_match:
                additional["договор"] = contract_match.group(1).strip()[:100]
                break
        
        # Срок оплаты
        payment_term_patterns = [
            r'[Сс]рок\s+оплаты[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
            r'[Оо]платить\s+до[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        ]
        for pattern in payment_term_patterns:
            term_match = re.search(pattern, text, re.IGNORECASE)
            if term_match:
                additional["срок_оплаты"] = term_match.group(1)
                break
        
        return additional
    
    def _merge_results(self, ml_result: Dict[str, Any], regex_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Объединяет результаты ML модели и regex парсинга
        
        Args:
            ml_result: Результаты ML модели
            regex_result: Результаты regex парсинга
            
        Returns:
            Объединенный результат
        """
        merged = regex_result.copy()
        
        # Добавляем поля из ML модели, если их нет в regex результате
        for key, value in ml_result.items():
            if key not in merged or not merged[key] or merged[key] == settings.UNRECOGNIZED_VALUE:
                if value:
                    merged[key] = value
            elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                # Объединяем вложенные словари
                for sub_key, sub_value in value.items():
                    if sub_key not in merged[key] or not merged[key][sub_key]:
                        merged[key][sub_key] = sub_value
        
        return merged

