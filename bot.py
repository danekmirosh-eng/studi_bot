import os
import logging
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Берём токен и chat_id из переменных окружения (Railway подставит их сам)
TOKEN = os.environ.get("TOKEN")
MOM_CHAT_ID = int(os.environ.get("MOM_CHAT_ID", "0"))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

data = {"duo": [], "eng": []}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для учёбы.\n\n"
        "Каждый день пиши:\n"
        "/duo <номер> — для Duolingo\n"
        "/eng <номер> — для English Galaxy\n\n"
        "Пример: /duo 5\n\n"
        "В воскресенье в 23:59 я пришлю отчёт."
    )


async def duo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши номер, например: /duo 5")
        return
    value = context.args[0]
    data["duo"].append(value)
    await update.message.reply_text(f"✅ Записал Duolingo: {value}")


async def eng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши номер, например: /eng 10")
        return
    value = context.args[0]
    data["eng"].append(value)
    await update.message.reply_text(f"✅ Записал English Galaxy: {value}")


async def send_report(context: ContextTypes.DEFAULT_TYPE):
    duo_str = ", ".join(data["duo"]) if data["duo"] else "нет отметок"
    eng_str = ", ".join(data["eng"]) if data["eng"] else "нет отметок"

    report = (
        "📊 Отчёт за неделю\n\n"
        f"🦉 Duolingo: {duo_str}\n"
        f"🚀 English Galaxy: {eng_str}"
    )

    await context.bot.send_message(chat_id=MOM_CHAT_ID, text=report)
    data["duo"].clear()
    data["eng"].clear()


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duo", duo))
    app.add_handler(CommandHandler("eng", eng))

    # Отчёт в воскресенье в 20:59 UTC = 23:59 по Москве
    app.job_queue.run_daily(
        send_report,
        time=time(hour=20, minute=59),
        days=(6,)
    )

    print("Бот запущен...")
    app.run_polling()