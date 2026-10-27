import json
import os
from threading import Thread
import telebot
from flask import Flask

# Твой токен бота
TOKEN = "ТВОЙ_ТОКЕН_БОТА"
bot = telebot.TeleBot(TOKEN)

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


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "Привет! Я твой файл-менеджер бот.\n\n"
      "📂 Отправь мне любой файл (документ), и я его сохраню.\n"
      "📋 Команда /files — посмотреть твои файлы.\n"
      "🗑 Команда /clear — очистить все файлы.",
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


# Обработка входящих документов (файлов)
@bot.message_handler(content_types=["document"])
def handle_document(message):
  user_id = str(message.from_user.id)
  file_name = message.document.file_name
  file_id = message.document.file_id

  if user_id not in user_files:
    user_files[user_id] = []

  # Сохраняем имя и file_id в список пользователя
  user_files[user_id].append({"file_name": file_name, "file_id": file_id})
  save_data(user_files)

  bot.reply_to(
      message,
      f"✅ Файл «{file_name}» успешно сохранен! Можешь посмотреть список через /files",
  )


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (обход ошибки портов) ---
app = Flask("")


@app.route("/")
def home():
  return "Bot is running 24/7!"


def run_web():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


if name == "main":
  # Запускаем веб-сервер в отдельном потоке
  t = Thread(target=run_web)
  t.start()

  # Запуск самого Telegram-бота
  print("Бот успешно запущен...")
  bot.infinity_polling()
