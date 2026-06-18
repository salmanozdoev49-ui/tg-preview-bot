import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
user_thumbs = {}  # хранит id обложки для каждого пользователя

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "1. Пришли фото с подписью /setpreview\n"
        "2. Пришли видео как файл — получишь его как медиа с твоей обложкой"
    )

async def set_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Запоминаем самое большое фото из сообщения
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

# Flask-приложение для вебхука
flask_app = Flask(__name__)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put(update)
    return "ok"

@flask_app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'^/setpreview$'), set_preview))
    app.add_handler(MessageHandler(filters.Document.VIDEO, video_handler))
    app.initialize()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
