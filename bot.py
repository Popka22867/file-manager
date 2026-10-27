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

# ID твоего приватного канала для сохранения файлов
STORAGE_CHANNEL_ID = -1004496422540

# Файл для хранения метаданных
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

# Получение username бота динамически
BOT_USERNAME = None
try:
    BOT_USERNAME = bot.get_me().username
except Exception:
    BOT_USERNAME = "your_bot"

# Команда /start (поддерживает выдачу файла по ссылке)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    
    # Если перешли по ссылке вида t.me/bot?start=get_index
    if len(args) > 1 and args[1].startswith("get_"):
        try:
            index = int(args[1].replace("get_", ""))
            if 0 <= index < len(files_db):
                file_item = files_db[index]
                bot.send_document(
                    message.chat.id, 
                    file_item['file_id'], 
                    caption=f"📁 Вот твой файл: *{file_item['name']}*", 
                    parse_mode="Markdown"
                )
                return
        except ValueError:
            pass

    # Обычный /start с кнопками
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

# Список файлов
@bot.message_handler(commands=['files'])
def list_files(message):
    if not files_db:
        bot.reply_to(message, "Пока нет сохраненных файлов.")
        return
    
    response = "📁 Список файлов и ссылки:\n\n"
    for idx, item in enumerate(files_db):
        link = f"https://t.me/{BOT_USERNAME}?start=get_{idx}"
        response += f"• *{item['name']}*\n🔗 {link}\n\n"
    bot.reply_to(message, response, parse_mode="Markdown")

# Очистка файлов (только для тебя)
@bot.message_handler(commands=['clear'])
def clear_files(message):
    global files_db
    if message.from_user.id != MY_ADMIN_ID:
        bot.reply_to(message, "Я не знаю такую команду.")
        return

    files_db = []
    save_data(files_db)
    bot.reply_to(message, "🗑 Все файлы удалены из базы.")

# Добавление файла через отправку документа с подписью
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    
    if user_id != MY_ADMIN_ID:
        return

    file_title = message.caption if message.caption else message.document.file_name
    
    try:
        # Пересылаем файл в твой приватный канал для вечного хранения
        forwarded_msg = bot.forward_message(STORAGE_CHANNEL_ID, message.chat.id, message.message_id)
        file_id = forwarded_msg.document.file_id
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при сохранении в канал. Убедись, что бот админ в канале!\nДетали: {e}")
        return

    files_db.append({"name": file_title, "file_id": file_id})
    save_data(files_db)

    new_index = len(files_db) - 1
    file_link = f"https://t.me/{BOT_USERNAME}?start=get_{new_index}"

    response = (
        f"✅ Файл успешно сохранен в канал!\n"
        f"📌 Название: *{file_title}*\n\n"
        f"🔗 Ссылка на скачивание:\n{file_link}"
    )
    bot.reply_to(message, response, parse_mode="Markdown")

# Обработка любой другой неизвестной команды или текста
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
