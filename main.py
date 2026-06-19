import os
import asyncio
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
user_thumbs = {}

async def start(update, context):
    await update.message.reply_text(
        "1. Пришли фото с подписью /setpreview\n"
        "2. Пришли видео как файл — получишь его как медиа с твоей обложкой"
    )

async def set_preview(update, context):
    user_thumbs[update.effective_user.id] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ Обложка сохранена. Теперь присылай видео файлом.")

async def video_handler(update, context):
    uid = update.effective_user.id
    if uid not in user_thumbs:
        await update.message.reply_text("⚠️ Сначала установи обложку: пришли фото с подписью /setpreview")
        return
    file_id = update.message.document.file_id
    await update.message.reply_video(
        video=file_id,
        thumb=user_thumbs[uid],
        supports_streaming=True
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'^/setpreview$'), set_preview))
app.add_handler(MessageHandler(filters.Document.VIDEO, video_handler))

# Запускаем polling в отдельном потоке, чтобы не блокировать Flask
def run_polling():
    asyncio.run(app.run_polling())

threading.Thread(target=run_polling, daemon=True).start()

# Flask для того, чтобы Render не ругался, что порт не слушает
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
