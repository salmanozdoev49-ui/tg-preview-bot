import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.environ["BOT_TOKEN"]
user_thumbs = {}

def start(update, context):
    update.message.reply_text(
        "1. Пришли фото с подписью /setpreview\n"
        "2. Пришли видео как файл — получишь его как медиа с твоей обложкой"
    )

def set_preview(update, context):
    file_id = update.message.photo[-1].file_id
    user_thumbs[update.effective_user.id] = file_id
    update.message.reply_text("✅ Обложка сохранена. Теперь присылай видео файлом.")

def video_handler(update, context):
    uid = update.effective_user.id
    if uid not in user_thumbs:
        update.message.reply_text("⚠️ Сначала установи обложку: пришли фото с подписью /setpreview")
        return
    file_id = update.message.document.file_id
    update.message.reply_video(
        video=file_id,
        thumb=user_thumbs[uid],
        supports_streaming=True
    )

updater = Updater(TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.photo & Filters.caption(r'^/setpreview$'), set_preview))
dp.add_handler(MessageHandler(Filters.document.video, video_handler))

flask_app = Flask(__name__)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    updater.update_queue.put(update)
    return "ok"

@flask_app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
