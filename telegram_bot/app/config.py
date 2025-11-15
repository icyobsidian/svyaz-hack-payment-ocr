"""
Конфигурация Telegram бота
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: str
    
    # Backend API URL
    BACKEND_URL: str = "http://backend:8000"
    
    # Спецфразы для ошибок
    ERROR_5XX_PHRASE: str = "Произошла внутренняя ошибка сервера. Попробуйте позже."
    ERROR_4XX_PHRASES: dict = {
        "400": "Неверный формат запроса. Пожалуйста, отправьте PDF файл.",
        "404": "Ресурс не найден.",
        "413": "Файл слишком большой. Пожалуйста, отправьте файл меньшего размера.",
        "415": "Неподдерживаемый тип файла. Пожалуйста, отправьте PDF файл.",
    }
    
    # Максимальный размер файла (в байтах) - 20 МБ
    MAX_FILE_SIZE: int = 20 * 1024 * 1024


# Глобальный экземпляр настроек
settings = Settings()

