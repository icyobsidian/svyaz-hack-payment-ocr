"""
Сервисы для взаимодействия с backend API
"""
import logging
from io import BytesIO
from typing import Dict, Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class PDFProcessorService:
    """Сервис для обработки PDF через backend API"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.endpoint = f"{self.backend_url}/api/v1/process-pdf"
    
    async def process_pdf(
        self, 
        file_bytes: BytesIO, 
        filename: str
    ) -> Dict[str, Any]:
        """
        Отправка PDF файла на обработку в backend
        
        Args:
            file_bytes: Байты PDF файла
            filename: Имя файла
            
        Returns:
            Словарь с результатом обработки:
            {
                "success": bool,
                "data": dict (если success=True),
                "status_code": int,
                "message": str (если success=False)
            }
        """
        try:
            # Подготовка данных для multipart/form-data
            file_bytes.seek(0)
            data = aiohttp.FormData()
            data.add_field(
                'file',
                file_bytes,
                filename=filename,
                content_type='application/pdf'
            )
            
            # Отправка запроса
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    status_code = response.status
                    
                    # Успешный ответ (2xx, 3xx)
                    if 200 <= status_code < 400:
                        try:
                            result_data = await response.json()
                            return {
                                "success": True,
                                "data": result_data,
                                "status_code": status_code
                            }
                        except Exception as e:
                            logger.error(f"Ошибка парсинга JSON ответа: {e}")
                            return {
                                "success": False,
                                "status_code": status_code,
                                "message": "Неверный формат ответа от сервера"
                            }
                    
                    # Ошибка (4xx, 5xx)
                    else:
                        try:
                            error_data = await response.json()
                            error_message = error_data.get("detail", error_data.get("message", ""))
                        except:
                            error_message = await response.text()
                        
                        return {
                            "success": False,
                            "status_code": status_code,
                            "message": error_message
                        }
                        
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при запросе к backend: {e}")
            return {
                "success": False,
                "status_code": 0,
                "message": f"Ошибка соединения с сервером: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
            return {
                "success": False,
                "status_code": 0,
                "message": f"Неожиданная ошибка: {str(e)}"
            }

