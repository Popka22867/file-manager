import json
import os
import telebot
from telebot.types import BotCommand

TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН"
CHANNEL_USERNAME = "@goat1488_67"
ADMIN_ID = 6795794125
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"

# Автовыбор пути: если есть Persistent Storage на HF, пишем в /data, иначе локально
if os.path.exists("/data"):
  DATA_FILE = "/data/files.json"
else:
  DATA_FILE = "files.json"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("add", "Добавить новый файл"),
    BotCommand("files", "Список всех файлов"),
    BotCommand("del", "Удалить файл по ключу"),
])

admin_states = {}


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return {}
  return {}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


def check_subscription(user_id):
  try:
    member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if member.status in ["member", "administrator", "creator"]:
      return True
  except Exception as e:
    print(f"Ошибка проверки подписки: {e}")
  return False


@bot.message_handler(commands=["start"])
def send_welcome(message):
  user_id = message.from_user.id
  args = message.text.split()

  if len(args) > 1:
    file_key = args[1]

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

    files_db = load_data()
    file_info = files_db.get(file_key)

    if file_info:
      file_id = file_info["file_id"]
      file_type = file_info["file_type"]
      description = file_info["description"]
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
    markup = telebot.types.InlineKeyboardMarkup()
    channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    btn_channel = telebot.types.InlineKeyboardButton(
        "📢 Наш канал", url=channel_link
    )
    btn_ls = telebot.types.InlineKeyboardButton("👤 Мое ЛС", url=FEEDBACK_BOT_URL)
    markup.add(btn_channel, btn_ls)

    caption_text = (
        "👋 Привет!\n\n"
        f"👀 Я храню файлы с канала {CHANNEL_USERNAME}\n\n"
        "✔️ Используй кнопки ниже для навигации"
    )

    try:
      with open("god.png", "rb") as photo:
        bot.send_photo(
            message.chat.id,
            photo,
            caption=caption_text,
            reply_markup=markup,
            parse_mode=None,
        )
    except Exception:
      bot.send_message(
          message.chat.id, caption_text, reply_markup=markup, parse_mode=None
      )


@bot.callback_query_handler(func=lambda call: call.data.startswith("check_sub_"))
def callback_check_sub(call):
  user_id = call.from_user.id
  file_key = call.data.split("_")[2]

  if check_subscription(user_id):
    bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
    bot.delete_message(call.message.chat.id, call.message.message_id)

    files_db = load_data()
    file_info = files_db.get(file_key)

    if file_info:
      file_id = file_info["file_id"]
      file_type = file_info["file_type"]
      description = file_info["description"]
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


@bot.message_handler(commands=["add"])
def add_file_step1(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
    return

  admin_states[ADMIN_ID] = "waiting_for_file"
  bot.send_message(
      message.chat.id,
      "📤 **Отправьте файл** (фото, документ или видео).\nВ описании (caption) укажи ключ и описание через пробел.\n\n*Пример:* `my_key Описание файла`",
      parse_mode="Markdown",
  )


@bot.message_handler(
    content_types=["document", "photo", "video"],
    func=lambda m: m.from_user.id == ADMIN_ID,
)
def handle_incoming_file(message):
  if admin_states.get(ADMIN_ID) != "waiting_for_file":
    return

  text = message.caption or message.text or ""
  parts = text.split(maxsplit=1)

  if not parts:
    bot.send_message(
        message.chat.id,
        "⚠️ Вы забыли указать ключ в описании. Попробуйте снова через команду"
        " /add",
    )
    admin_states.pop(ADMIN_ID, None)
    return

  key = parts[0]
  description = parts[1] if len(parts) > 1 else ""

  file_id = None
  file_type = "unknown"

  if message.document:
    file_id = message.document.file_id
    file_type = "document"
  elif message.photo:
    file_id = message.photo[-1].file_id
    file_type = "photo"
  elif message.video:
    file_id = message.video.file_id
    file_type = "video"

  files_db = load_data()
  files_db[key] = {
      "file_id": file_id,
      "file_type": file_type,
      "description": description,
  }
  save_data(files_db)

  bot_username = bot.get_me().username
  deep_link = f"https://t.me/{bot_username}?start={key}"

  bot.send_message(
      message.chat.id,
      f"✅ Файл успешно добавлен!\n\n🔑 Ключ: `{key}`\n🔗 Ссылка для выдачи:\n{deep_link}",
      parse_mode=None,
  )
  admin_states.pop(ADMIN_ID, None)


@bot.message_handler(commands=["files"])
def list_files(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
    return

  files_db = load_data()

  if not files_db:
    bot.send_message(message.chat.id, "📭 Список файлов пуст.")
    return

  text = "📂 Список сохраненных файлов:\n\n"
  for key, info in files_db.items():
    desc = info.get("description", "")
    text += f"• `{key}` — {desc if desc else 'Без описания'}\n"

  bot.send_message(message.chat.id, text, parse_mode=None)


@bot.message_handler(commands=["del"])
def delete_file(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
    return

  args = message.text.split(maxsplit=1)
  if len(args) < 2:
    bot.send_message(
        message.chat.id,
        "⚠️ Укажите ключ файла для удаления. Пример: `/del my_key`",
        parse_mode="Markdown",
    )
    return

  key = args[1]
  files_db = load_data()

  if key in files_db:
    del files_db[key]
    save_data(files_db)
    bot.send_message(
        message.chat.id, f"🗑 Файл с ключом `{key}` удален.", parse_mode=None
    )
  else:
    bot.send_message(
        message.chat.id, f"❌ Файл с ключом `{key}` не найден.", parse_mode=None
    )


print("Бот запущен с файловым хранилищем...")
bot.infinity_polling()
