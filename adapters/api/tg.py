from config import TG_CHAT_ID, TG_TOKEN
import telegram
import asyncio


def send_message(message: str) -> None:
    """Отправка сообщения в телеграм."""

    bot = telegram.Bot(token=TG_TOKEN)
    asyncio.run(bot.send_message(TG_CHAT_ID, message))
