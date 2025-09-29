import json
import random
import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, ContextTypes
from telegram.ext import JobQueue

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
INTERVAL = int(os.getenv('INTERVAL', 21600)) 
CHANNEL_ID = os.getenv('CHANNEL_ID')
QUOTES_FILE = "bulgakov_quotes.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

try:
    with open(QUOTES_FILE, encoding="utf-8") as f:
        QUOTES = json.load(f)
    logger.info(f"Загружено {len(QUOTES)} цитат")
except FileNotFoundError:
    logger.error(f"Файл {QUOTES_FILE} не найден!")
    QUOTES = ["Цитаты не загружены"]
except json.JSONDecodeError:
    logger.error(f"Ошибка чтения JSON из {QUOTES_FILE}")
    QUOTES = ["Ошибка загрузки цитат"]


async def send_quote(context: ContextTypes.DEFAULT_TYPE):
    if not QUOTES:
        logger.error("Нет цитат для отправки")
        return
    
    quote = random.choice(QUOTES)
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=quote)
        logger.info(f"Цитата отправлена в {CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")


def main():
    if not TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте файл .env")
        return
    
    if not CHANNEL_ID:
        logger.error("CHANNEL_ID не установлен! Проверьте файл .env")
        return

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.job_queue.run_repeating(
        send_quote,
        interval=INTERVAL,
        first=10  
    )

    logger.info(f"Бот запущен. Отправка цитат каждые {INTERVAL} секунд в {CHANNEL_ID}")

    application.run_polling()


if __name__ == "__main__":
    main()
