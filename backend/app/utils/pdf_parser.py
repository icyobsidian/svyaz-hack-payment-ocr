"""
Утилиты для парсинга PDF файлов
"""
import logging
from io import BytesIO
from typing import Optional, List, Tuple

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDFParser:
    """Парсер для извлечения текста из PDF"""
    
    def __init__(self):
        self.parser_method = self._detect_best_parser()
    
    def _detect_best_parser(self) -> str:
        """Определяет лучший доступный парсер"""
        if PYMUPDF_AVAILABLE:
            return "pymupdf"
        elif PDFPLUMBER_AVAILABLE:
            return "pdfplumber"
        else:
            raise ImportError(
                "Не установлены библиотеки для парсинга PDF. "
                "Установите PyMuPDF или pdfplumber."
            )
    
    def extract_text(self, pdf_bytes: BytesIO) -> str:
        """
        Извлекает текст из PDF
        
        Args:
            pdf_bytes: Байты PDF файла
            
        Returns:
            Извлеченный текст
        """
        pdf_bytes.seek(0)
        
        if self.parser_method == "pymupdf":
            return self._extract_with_pymupdf(pdf_bytes)
        elif self.parser_method == "pdfplumber":
            return self._extract_with_pdfplumber(pdf_bytes)
    
    def _extract_with_pymupdf(self, pdf_bytes: BytesIO) -> str:
        """Извлечение текста с помощью PyMuPDF"""
        pdf_bytes.seek(0)
        doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_parts.append(text)
        
        doc.close()
        return "\n".join(text_parts)
    
    def _extract_with_pdfplumber(self, pdf_bytes: BytesIO) -> str:
        """Извлечение текста с помощью pdfplumber"""
        pdf_bytes.seek(0)
        text_parts = []
        
        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n".join(text_parts)
    
    def extract_text_with_positions(self, pdf_bytes: BytesIO) -> List[Tuple[str, dict]]:
        """
        Извлекает текст с позициями (для более точного извлечения)
        
        Returns:
            Список кортежей (текст, позиция)
        """
        pdf_bytes.seek(0)
        
        if self.parser_method == "pymupdf":
            return self._extract_positions_pymupdf(pdf_bytes)
        elif self.parser_method == "pdfplumber":
            return self._extract_positions_pdfplumber(pdf_bytes)
    
    def _extract_positions_pymupdf(self, pdf_bytes: BytesIO) -> List[Tuple[str, dict]]:
        """Извлечение текста с позициями через PyMuPDF"""
        pdf_bytes.seek(0)
        doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")
        results = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            bbox = span["bbox"]
                            results.append((
                                text,
                                {
                                    "page": page_num,
                                    "bbox": bbox,
                                    "font": span.get("font", ""),
                                    "size": span.get("size", 0)
                                }
                            ))
        
        doc.close()
        return results
    
    def _extract_positions_pdfplumber(self, pdf_bytes: BytesIO) -> List[Tuple[str, dict]]:
        """Извлечение текста с позициями через pdfplumber"""
        pdf_bytes.seek(0)
        results = []
        
        with pdfplumber.open(pdf_bytes) as pdf:
            for page_num, page in enumerate(pdf.pages):
                words = page.extract_words()
                for word in words:
                    results.append((
                        word["text"],
                        {
                            "page": page_num,
                            "bbox": (word["x0"], word["top"], word["x1"], word["bottom"]),
                            "font": word.get("fontname", ""),
                            "size": word.get("size", 0)
                        }
                    ))
        
        return results

