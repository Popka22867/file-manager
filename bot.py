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
        return {}
  return {}


# Сохранение данных в json
def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Инициализация хранилища
user_files = load_data()


# Команда /start с обновленными ссылками
@bot.message_handler(commands=["start"])
def send_welcome(message):
  markup = InlineKeyboardMarkup()
  btn_channel = InlineKeyboardButton(
      "📢 Мой канал", url="https://t.me/Goat1488_67"
  )
  btn_feedback = InlineKeyboardButton(
      "💬 Бот обратной связи", url="https://t.me/feedbackls_bot"
  )
  markup.add(btn_channel, btn_feedback)

  bot.reply_to(
      message,
      "Привет! Я твой файл-менеджер бот.\n\n"
      "📂 Отправь мне любой файл (документ), и я надежно сохраню его в базу.\n"
      "📋 Команда /files — посмотреть твои файлы.\n"
      "🆔 Команда /myid — узнать свой Telegram ID.\n"
      "🗑 Команда /clear — очистить все твои сохраненные файлы.",
      reply_markup=markup,
  )


# Узнать свой ID
@bot.message_handler(commands=["myid"])
def show_my_id(message):
  user_id = message.from_user.id
  username = message.from_user.username
  bot.reply_to(
      message,
      f"👤 Твои данные:\nID: `{user_id}`\nUsername: @{username}",
      parse_mode="Markdown",
  )


# Просмотр сохраненных файлов
@bot.message_handler(commands=["files"])
def list_files(message):
  user_id = str(message.from_user.id)

  if user_id not in user_files or not user_files[user_id]:
    bot.reply_to(message, "У тебя пока нет сохраненных файлов.")
    return

  response = "📁 Твои сохраненные файлы:\n\n"
  for index, file_info in enumerate(user_files[user_id], 1):
    response += f"{index}. {file_info['file_name']}\n"

  bot.reply_to(message, response)


# Очистка всех файлов пользователя
@bot.message_handler(commands=["clear"])
def clear_files(message):
  user_id = str(message.from_user.id)

  if user_id in user_files:
    user_files[user_id] = []
    save_data(user_files)
    bot.reply_to(message, "🗑 Все твои файлы были успешно удалены из базы.")
  else:
    bot.reply_to(message, "У тебя и так нет сохраненных файлов.")


# Обработка входящих документов (файлов) с записью в files.json
@bot.message_handler(content_types=["document"])
def handle_document(message):
  user_id = str(message.from_user.id)
  file_name = message.document.file_name
  file_id = message.document.file_id

  if user_id not in user_files:
    user_files[user_id] = []

  user_files[user_id].append({"file_name": file_name, "file_id": file_id})
  save_data(user_files)

  bot.reply_to(
      message,
      f"✅ Файл «{file_name}» успешно сохранен в files.json! Можешь посмотреть список через /files",
  )


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (обход ошибки портов) ---
app = Flask("")


@app.route("/")
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
