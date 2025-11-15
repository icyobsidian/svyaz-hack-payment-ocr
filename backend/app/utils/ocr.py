"""
Утилиты для OCR (Optical Character Recognition)
"""
import logging
from io import BytesIO
from typing import Optional, Tuple
import tempfile
import os

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from ..config import settings

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Процессор для OCR обработки изображений"""
    
    def __init__(self):
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "Tesseract OCR не установлен. "
                "Установите: pip install pytesseract pillow"
            )
    
    def extract_text_from_image(self, image_bytes: BytesIO, language: Optional[str] = None) -> str:
        """
        Извлекает текст из изображения с помощью OCR
        
        Args:
            image_bytes: Байты изображения
            language: Язык для OCR (по умолчанию из настроек)
            
        Returns:
            Извлеченный текст
        """
        image_bytes.seek(0)
        image = Image.open(image_bytes)
        
        lang = language or settings.OCR_LANGUAGE
        
        # Конфигурация Tesseract
        custom_config = f'--psm {settings.OCR_PSM}'
        
        try:
            text = pytesseract.image_to_string(image, lang=lang, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"Ошибка OCR: {e}")
            return ""
    
    def pdf_to_images(self, pdf_bytes: BytesIO) -> list:
        """
        Конвертирует PDF в изображения для OCR
        
        Args:
            pdf_bytes: Байты PDF файла
            
        Returns:
            Список байтов изображений
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF не установлен для конвертации PDF в изображения")
        
        pdf_bytes.seek(0)
        doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Конвертация страницы в изображение (300 DPI для лучшего качества)
            mat = fitz.Matrix(300/72, 300/72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            images.append(BytesIO(img_bytes))
        
        doc.close()
        return images
    
    def extract_text_from_pdf_images(self, pdf_bytes: BytesIO) -> str:
        """
        Извлекает текст из PDF через OCR (для сканированных документов)
        
        Args:
            pdf_bytes: Байты PDF файла
            
        Returns:
            Извлеченный текст
        """
        images = self.pdf_to_images(pdf_bytes)
        text_parts = []
        
        for img_bytes in images:
            text = self.extract_text_from_image(img_bytes)
            if text.strip():
                text_parts.append(text)
        
        return "\n".join(text_parts)

