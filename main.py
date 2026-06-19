import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Defaults

TOKEN = os.environ["BOT_TOKEN"]
user_thumbs = {}

# Создаём приложение
app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "1. Пришли фото с подписью /setpreview\n"
        "2. Пришли видео как файл — получишь его как медиа с твоей обложкой"
    )

async def set_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_thumbs[update.effective_user.id] = update.message.photo[-1].file_id
    await update.message.reply_text("✅ Обложка сохранена. Теперь присылай видео файлом.")

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'^/setpreview$'), set_preview))
app.add_handler(MessageHandler(filters.Document.VIDEO, video_handler))

# Инициализируем приложение один раз при старте
import asyncio
asyncio.run(app.initialize())

# Flask-приложение
flask_app = Flask(__name__)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    # Получаем обновление
    update = Update.de_json(request.get_json(force=True), app.bot)
    # Обрабатываем его синхронно через process_update (не async)
    app.process_update(update)
    return "ok"

@flask_app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    # Запускаем Flask (вебхук)
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
