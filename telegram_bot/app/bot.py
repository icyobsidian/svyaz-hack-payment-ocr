"""
Главный файл для запуска Telegram бота
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import settings
from .handlers import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    # Проверка наличия токена
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        sys.exit(1)
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(router)
    
    logger.info("Бот запущен и готов к работе!")
    logger.info(f"Backend URL: {settings.BACKEND_URL}")
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

