"""
Конфигурация Backend API
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # API настройки
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Payment OCR Service"
    VERSION: str = "1.0.0"
    
    # Спецслово для нераспознанных значений
    UNRECOGNIZED_VALUE: str = "НЕ_РАСПОЗНАНО"
    
    # Настройки обработки файлов
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 МБ
    ALLOWED_EXTENSIONS: list = [".pdf"]
    
    # OCR настройки
    OCR_LANGUAGE: str = "rus+eng"  # Русский и английский
    OCR_PSM: int = 6  # Page segmentation mode для Tesseract
    
    # Логирование
    LOG_LEVEL: str = "INFO"


# Глобальный экземпляр настроек
settings = Settings()

