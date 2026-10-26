import sqlite3
import telebot

TOKEN = "8919124931:AAH1kn9Ib5iwU4bR5513Hc7ZsWqvbCIE_io"
CHANNEL_ID = "@goat1488_67"

# Твой Telegram ID добавлен в список админов
ADMIN_IDS = [6795794125]

bot = telebot.TeleBot(TOKEN)


# Инициализация базы данных
def init_db():
  conn = sqlite3.connect("bot_files.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            key TEXT PRIMARY KEY,
            file_id TEXT,
            file_type TEXT,
            caption TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


def check_subscription(user_id):
  try:
    member = bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in ["creator", "administrator", "member"]
  except Exception:
    return False


# --- АДМИН-ПАНЕЛЬ (Загрузка и управление файлами) ---


@bot.message_handler(content_types=["document", "video", "audio", "photo"])
def handle_admin_file(message):
  if message.from_user.id not in ADMIN_IDS:
    return

  caption = message.caption or ""
  if caption.startswith("/add"):
    parts = caption.split(maxsplit=2)
    if len(parts) < 2:
      bot.reply_to(
          message, "⚠️ Формат: отправь файл с подписью /add ключ описание"
      )
      return

    key = parts[1]
    file_caption = parts[2] if len(parts) > 2 else ""

    if message.document:
      file_id = message.document.file_id
      file_type = "document"
    elif message.video:
      file_id = message.video.file_id
      file_type = "video"
    elif message.audio:
      file_id = message.audio.file_id
      file_type = "audio"
    elif message.photo:
      file_id = message.photo[-1].file_id
      file_type = "photo"
    else:
      return

    conn = sqlite3.connect("bot_files.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO files (key, file_id, file_type, caption) VALUES"
        " (?, ?, ?, ?)",
        (key, file_id, file_type, file_caption),
    )
    conn.commit()
    conn.close()

    bot.reply_to(
        message,
        f"✅ Файл успешно сохранен!\n🔑 Ключ: {key}\n🔗 Ссылка для"
        f" выдачи: https://t.me/goat1488_67_bot?start={key}",
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["files"])
def list_files(message):
  if message.from_user.id not in ADMIN_IDS:
    return
  conn = sqlite3.connect("bot_files.db")
  cursor = conn.cursor()
  cursor.execute("SELECT key, caption, file_type FROM files")
  rows = cursor.fetchall()
  conn.close()

  if not rows:
    bot.send_message(message.chat.id, "📭 База файлов пуста.")
    return

  text = "📁 Список загруженных файлов:\n\n"
  for row in rows:
    text += (
        f"🔑 Ключ: {row[0]}\n📝 Описание: {row[1]}\n📌 Тип:"
        f" {row[2]}\n------------------\n"
    )
  bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["del"])
def delete_file(message):
  if message.from_user.id not in ADMIN_IDS:
    return
  parts = message.text.split()
  if len(parts) < 2:
    bot.reply_to(message, "⚠️ Использование: /del ключ", parse_mode="Markdown")
    return
  key = parts[1]
  conn = sqlite3.connect("bot_files.db")
  cursor = conn.cursor()
  cursor.execute("DELETE FROM files WHERE key = ?", (key,))
  conn.commit()
  conn.close()
  bot.reply_to(
      message, f"🗑 Файл с ключом {key} удален.", parse_mode="Markdown"
  )


# --- ПОЛЬЗОВАТЕЛЬСКАЯ ЧАСТЬ ---


@bot.message_handler(commands=["start"])
def handle_start(message):
  user_id = message.from_user.id

  if not check_subscription(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}"
        )
    )
    markup.add(
        telebot.types.InlineKeyboardButton(
            "✅ Я подписался", callback_data="check_sub"
        )
    )
    bot.send_message(
        message.chat.id,
        "Привет! Я бот-файловый менеджер.\nЧтобы пользоваться мной, подпишись"
        " на наш канал:",
        reply_markup=markup,
    )
    return
    command_parts = message.text.split()
  if len(command_parts) > 1:
    key = command_parts[1]

    conn = sqlite3.connect("bot_files.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT file_id, file_type, caption FROM files WHERE key = ?", (key,)
    )
    file_data = cursor.fetchone()
    conn.close()

    if file_data:
      file_id, file_type, caption = file_data
      if file_type == "document":
        bot.send_document(message.chat.id, file_id, caption=caption)
      elif file_type == "video":
        bot.send_video(message.chat.id, file_id, caption=caption)
      elif file_type == "audio":
        bot.send_audio(message.chat.id, file_id, caption=caption)
      elif file_type == "photo":
        bot.send_photo(message.chat.id, file_id, caption=caption)
    else:
      bot.send_message(
          message.chat.id, "❌ Файл по этой ссылке не найден или был удален."
      )
  else:
    bot.send_message(
        message.chat.id,
        "Привет! Используй специальную ссылку из поста, чтобы получить файл.",
    )


@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_sub(call):
  if check_subscription(call.from_user.id):
    bot.answer_callback_query(call.id, "Спасибо за подписку!")
    bot.edit_message_text(
        "Подписка подтверждена! Теперь перейдите по ссылке файла снова.",
        call.message.chat.id,
        call.message.message_id,
    )
  else:
    bot.answer_callback_query(
        call.id, "Ты еще не подписался на канал!", show_alert=True
    )


bot.infinity_polling()