import json
import os
from threading import Thread
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

# Твой токен бота
TOKEN = "8847975926:AAGmu4pfRfMa11Ow4hCw0kFURveuFI2YYPw"
bot = telebot.TeleBot(TOKEN)

# Твой фиксированный ID администратора
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

# Временное хранилище для ожидания файла после команды /add
waiting_for_file = {}

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

# Команда /files — список файлов
@bot.message_handler(commands=['files'])
def list_files(message):
    if not files_db:
        bot.reply_to(message, "Пока нет сохраненных файлов.")
        return
    
    response = "📁 Список файлов:\n\n"
    for idx, item in enumerate(files_db, 1):
        response += f"{idx}. {item['name']}\n"
    bot.reply_to(message, response)

# Команда /clear — очистка файлов (только для тебя)
@bot.message_handler(commands=['clear'])
def clear_files(message):
    global files_db
    if message.from_user.id != MY_ADMIN_ID:
        bot.reply_to(message, "Я не знаю такую команду.")
        return

    files_db = []
    save_data(files_db)
    bot.reply_to(message, "🗑 Все файлы удалены.")

# Команда /add [название] — только для тебя
@bot.message_handler(commands=['add'])
def add_file_command(message):
    if message.from_user.id != MY_ADMIN_ID:
        bot.reply_to(message, "Я не знаю такую команду.")
        return

    # Извлекаем название после команды /add
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Напиши название после команды, например: `/add have a hat`", parse_mode="Markdown")
        return

    file_title = parts[1].strip()
    waiting_for_file[message.from_user.id] = file_title
    bot.reply_to(message, f"📥 Отправь файл для сохранения под названием: *{file_title}*", parse_mode="Markdown")

# Обработка входящих документов (файлов)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    
    # Проверяем, что файл отправляет именно админ и он вызывал команду /add
    if user_id != MY_ADMIN_ID or user_id not in waiting_for_file:
        return

    file_title = waiting_for_file.pop(user_id)
    file_id = message.document.file_id

    files_db.append({"name": file_title, "file_id": file_id})
    save_data(files_db)

    bot.reply_to(message, f"✅ Файл успешно сохранен под названием: *{file_title}*", parse_mode="Markdown")

# Обработка любой другой неизвестной хуйни/текста
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
