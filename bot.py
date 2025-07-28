import json
import random
import logging
from telegram.ext import Application, ContextTypes
from telegram.ext import JobQueue

TOKEN = "7992974712:AAHXv36l706k70brvuMnJrqzWRyK2Wbf1Ko"
INTERVAL = 21600  
CHANNEL_ID = "@bulgakoveveryday"
QUOTES_FILE = "bulgakov_quotes.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

with open(QUOTES_FILE, encoding="utf-8") as f:
    QUOTES = json.load(f)


async def send_quote(context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=quote)


def main():
    application = (
        Application.builder()
        .token(TOKEN)
        .job_queue(JobQueue())
        .build()
    )

    application.job_queue.run_repeating(
        send_quote,
        interval=INTERVAL,
        first=0
    )

    logger.info(f"Бот запущен. Отправка цитат каждые {INTERVAL} секунд в {CHANNEL_ID}")

    application.run_polling()


if __name__ == "__main__":
    main()
