import sqlite3
import telebot

# Твои данные
TOKEN = "8919124931:AAH1kn9Ib5iwU4bR5513Hc7ZsWqvbCIE_io"
CHANNEL_USERNAME = "@goat1488_67"  # Канал, на который нужна подписка
ADMIN_ID = 6795794125  # Твой Telegram ID

bot = telebot.TeleBot(TOKEN)

# Инициализация базы данных SQLite
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS files (
    key TEXT PRIMARY KEY,
    file_id TEXT,
    file_type TEXT,
    description TEXT
)
"""
)
conn.commit()


# Функция проверки подписки
def check_subscription(user_id):
  try:
    member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    # Статусы, при которых считается, что пользователь подписан
    if member.status in ["member", "administrator", "creator"]:
      return True
  except Exception as e:
    print(f"Ошибка проверки подписки: {e}")
  return False


# Команда /start (с поддержкой глубоких ссылок)
@bot.message_handler(commands=["start"])
def send_welcome(message):
  user_id = message.from_user.id
  args = message.text.split()

  # Если пользователь пришел по глубокой ссылке (например, /start key123)
  if len(args) > 1:
    file_key = args[1]

    # Проверяем подписку
    if not check_subscription(user_id):
      markup = telebot.types.InlineKeyboardMarkup()
      channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
      btn_channel = telebot.types.InlineKeyboardButton(
          "📢 Подписаться на канал", url=channel_link
      )
      btn_check = telebot.types.InlineKeyboardButton(
          "✅ Я подписался", callback_data=f"check_sub_{file_key}"
      )
      markup.add(btn_channel)
      markup.add(btn_check)

      bot.send_message(
          message.chat.id,
          "❌ Чтобы получить файл, вы должны быть подписаны на наш канал!",
          reply_markup=markup,
      )
      return

    # Если подписан — выдаем файл
    cursor.execute(
        "SELECT file_id, file_type, description FROM files WHERE key = ?",
        (file_key,),
    )
    row = cursor.fetchone()

    if row:
      file_id, file_type, description = row
      caption = f"📁 {description}" if description else ""

      if file_type == "document":
        bot.send_document(user_id, file_id, caption=caption)
      elif file_type == "photo":
        bot.send_photo(user_id, file_id, caption=caption)
      elif file_type == "video":
        bot.send_video(user_id, file_id, caption=caption)
      else:
        bot.send_message(user_id, f"📄 {description}\n\nФайл: {file_id}")
    else:
      bot.send_message(message.chat.id, "❌ Файл не найден или был удален.")
  else:
    bot.send_message(
        message.chat.id,
        "Привет! Этот бот выдает файлы за подписку на канал."
        f" {CHANNEL_USERNAME}",
    )


# Обработка нажатия на кнопку «Я подписался»
@bot.callback_query_handler(func=lambda call: call.data.startswith("check_sub_"))
def callback_check_sub(call):
  user_id = call.from_user.id
  file_key = call.data.split("_")[2]

  if check_subscription(user_id):
    bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # Выдаем файл после успешной проверки
    cursor.execute(
        "SELECT file_id, file_type, description FROM files WHERE key = ?",
        (file_key,),
    )
    row = cursor.fetchone()

    if row:
      file_id, file_type, description = row
      caption = f"📁 {description}" if description else ""

      if file_type == "document":
        bot.send_document(user_id, file_id, caption=caption)
      elif file_type == "photo":
        bot.send_photo(user_id, file_id, caption=caption)
      elif file_type == "video":
        bot.send_video(user_id, file_id, caption=caption)
  else:
    bot.answer_callback_query(
        call.id, "❌ Вы все еще не подписаны на канал!", show_alert=True
    )
# Админ-команда: Добавление файла (/add ключ описание)
@bot.message_handler(commands=["add"])
def add_file(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
    return

  if not message.reply_to_message:
    bot.send_message(
        message.chat.id,
        "⚠️ Ответьте этой командой (/add ключ описание) на нужное сообщение с"
        " файлом (документ, фото или видео).",
    )
    return

  # Исправлено: корректное разбиение команды на части с защитой от ошибок
  command_parts = message.text.split(maxsplit=2)
  if len(command_parts) < 2:
    bot.send_message(
        message.chat.id,
        "⚠️ Укажите ключ для файла. Пример: /add my_key Описание файла",
    )
    return

  key = command_parts[1]
  description = command_parts[2] if len(command_parts) > 2 else ""

  replied = message.reply_to_message
  file_id = None
  file_type = "unknown"

  if replied.document:
    file_id = replied.document.file_id
    file_type = "document"
  elif replied.photo:
    file_id = replied.photo[-1].file_id
    file_type = "photo"
  elif replied.video:
    file_id = replied.video.file_id
    file_type = "video"
  else:
    bot.send_message(
        message.chat.id,
        "❌ В отвеченном сообщении нет поддерживаемого файла (документ, фото,"
        " видео).",
    )
    return

  try:
    cursor.execute(
        "REPLACE INTO files (key, file_id, file_type, description) VALUES"
        " (?, ?, ?, ?)",
        (key, file_id, file_type, description),
    )
    conn.commit()

    bot_username = bot.get_me().username
    deep_link = f"https://t.me/{bot_username}?start={key}"
    bot.send_message(
        message.chat.id,
        f"✅ Файл успешно добавлен!\n\n🔑 Ключ: {key}\n🔗 Ссылка для"
        f" выдачи:\n{deep_link}",
        parse_mode="Markdown",
    )
  except Exception as e:
    bot.send_message(message.chat.id, f"❌ Ошибка базы данных: {e}")


# Админ-команда: Список всех файлов (/files)
@bot.message_handler(commands=["files"])
def list_files(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
    return

  cursor.execute("SELECT key, description FROM files")
  rows = cursor.fetchall()

  if not rows:
    bot.send_message(message.chat.id, "📭 База данных пуста.")
    return

  text = "📂 Список сохраненных файлов:\n\n"
  for key, desc in rows:
    text += f"• {key} — {desc if desc else 'Без описания'}\n"

  bot.send_message(message.chat.id, text, parse_mode="Markdown")


# Админ-команда: Удаление файла (/del ключ)
@bot.message_handler(commands=["del"])
def delete_file(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
    return

  args = message.text.split(maxsplit=1)
  if len(args) < 2:
    bot.send_message(
        message.chat.id, "⚠️ Укажите ключ файла для удаления. Пример: /del my_key"
    )
    return

  key = args[1]
  cursor.execute("DELETE FROM files WHERE key = ?", (key,))
  conn.commit()

  bot.send_message(
      message.chat.id, f"🗑 Файл с ключом {key} удален (если он существовал)."
  )


print("Бот запущен...")
bot.infinity_polling()
