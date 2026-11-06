import fcntl
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

LOCK_PATH = Path(__file__).with_name(".bot.lock")


def acquire_single_instance_lock():
    handle = LOCK_PATH.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise SystemExit("Бот уже запущен. Останови другой процесс, прежде чем стартовать новый.")
    return handle


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    await message.reply_text("Привет. Напиши сообщение — я отвечу.")


async def reply_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.text is None:
        return
    await message.reply_text(f"Ты написал: {message.text}")


async def reply_to_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    await message.reply_text("Я пока отвечаю только на текст. Напиши сообщение словами.")


def main() -> None:
    lock = acquire_single_instance_lock()
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("Задай BOT_TOKEN в .env или в окружении. Пример есть в .env.example.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_text))
    app.add_handler(MessageHandler(~filters.TEXT & ~filters.COMMAND, reply_to_other))
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        lock.close()


if __name__ == "__main__":
    main()
