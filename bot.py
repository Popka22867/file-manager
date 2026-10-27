import json
import os
from threading import Thread
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

# Твой токен бота
TOKEN = "8847975926:AAGmu4pfRfMa11Ow4hCw0kFURveuFI2YYPw"
bot = telebot.TeleBot(TOKEN)

# Твой фиксированный ID
MY_ADMIN_ID = 6795794125

# Файл для хранения данных
DATA_FILE = "files.json"

# Загрузка данных из json
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Сохранение данных в json
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

files_db = load_data()

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    btn_channel = InlineKeyboardButton("📢 Мой Telegram-канал", url="https://t.me/Goat1488_67")
    btn_feedback = InlineKeyboardButton("💬 Бот обратной связи", url="https://t.me/feedbackls_bot")
    markup.add(btn_channel)
    markup.add(btn_feedback)

    text = (
        "Я бот-файловый менеджер.\n\n"
        "Перейди по ссылке в Telegram-канале или воспользуйся кнопками ниже для навигации."
    )
    bot.reply_to(message, text, reply_markup=markup)

# Просмотр файлов
@bot.message_handler(commands=['files'])
def list_files(message):
    if not files_db:
        bot.reply_to(message, "Пока нет сохраненных файлов.")
        return
    
    response = "📁 Список файлов:\n\n"
    for idx, item in enumerate(files_db, 1):
        response += f"{idx}. {item['name']}\n"
    bot.reply_to(message, response)

# Очистка файлов (только для админа)
@bot.message_handler(commands=['clear'])
def clear_files(message):
    global files_db
    if message.from_user.id == MY_ADMIN_ID:
        files_db = []
        save_data(files_db)
        bot.reply_to(message, "🗑 Все файлы удалены.")
    else:
        bot.reply_to(message, "У тебя нет прав на это действие.")

# Добавление файла (отправляешь документ с подписью-названием, например: have a hat)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_name = message.caption if message.caption else message.document.file_name
    file_id = message.document.file_id

    files_db.append({"name": file_name, "file_id": file_id})
    save_data(files_db)

    bot.reply_to(message, f"✅ Файл успешно добавлен под названием: {file_name}")

# Обработка любой непонятной хуйни / текста / команд
@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.reply_to(message, "Я не знаю такую команду.")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    
    print("Бот успешно запущен...")
    bot.infinity_polling()
