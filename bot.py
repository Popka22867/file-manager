import json
import os
from threading import Thread
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

TOKEN = "8847975926:AAGmu4pfRfMa11Ow4hCw0kFURveuFI2YYPw"
CHANNEL_USERNAME = "@goat1488_67"
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"
MAPPING_FILE = "file_mapping.json"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("add", "Добавить новый файл"),
    BotCommand("files", "Список всех файлов"),
    BotCommand("del", "Удалить файл по тегу"),
])

admin_states = {}

def load_mapping():
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_mapping(tag, data):
    mapping = load_mapping()
    mapping[tag] = data
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)

def delete_mapping(tag):
    mapping = load_mapping()
    if tag in mapping:
        del mapping[tag]
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)

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
            markup = InlineKeyboardMarkup()
            channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
            markup.add(InlineKeyboardButton("📢 Подписаться на канал", url=channel_link))
            markup.add(InlineKeyboardButton("✅ Я подписался", callback_data=f"check_sub_{file_key}"))

            bot.send_message(
                message.chat.id,
                "❌ Чтобы получить файл, вы должны быть подписаны на наш канал!",
                reply_markup=markup,
            )
            return

        send_file_to_user(message.chat.id, file_key)
        return

    markup = InlineKeyboardMarkup()
    channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    btn_channel = InlineKeyboardButton("📢 Наш канал", url=channel_link)
    btn_ls = InlineKeyboardButton("👤 Мое ЛС", url=FEEDBACK_BOT_URL)
    markup.add(btn_channel, btn_ls)

    caption_text = (
        "👋 Привет!\n\n"
        f"👀 Я храню файлы с канала {CHANNEL_USERNAME}\n\n"
        "✔️ Используй кнопки ниже для навигации"
    )

    try:
        with open("god.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_sub_"))
def callback_check_sub(call):
    user_id = call.from_user.id
    file_key = call.data.split("_")[2]

    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_file_to_user(user_id, file_key)
    else:
        bot.answer_callback_query(call.id, "❌ Вы все еще не подписаны на канал!", show_alert=True)

def send_file_to_user(chat_id, file_key):
    bot.send_message(chat_id, "Секунду...")
    
    mapping = load_mapping()
    if file_key in mapping:
        item = mapping[file_key]
        try:
            bot.copy_message(chat_id, STORAGE_CHANNEL_ID, item['msg_id'])
            return
        except Exception:
            pass

    bot.send_message(chat_id, "❌ Файл не найден.")

@bot.message_handler(commands=["add"])
def add_file_step1(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
        return

    admin_states[ADMIN_ID] = "waiting_for_file"
    bot.send_message(
        message.chat.id,
        "📤 **Отправьте файл**.\nВ описании к файлу (caption) укажи данные в формате:\n\n"
        "`тег Описание файла`\n\n*Пример:* `gold Лучший кфг`",
        parse_mode="Markdown",
    )

@bot.message_handler(content_types=["document", "photo", "video"], func=lambda m: m.from_user.id == ADMIN_ID)
def handle_incoming_file(message):
    if admin_states.get(ADMIN_ID) != "waiting_for_file":
        return

    text = message.caption or ""
    parts = text.split(maxsplit=1)

    if not parts:
        bot.send_message(
            message.chat.id,
            "⚠️ Вы забыли указать тег в описании к файлу. Попробуйте снова через команду /add",
        )
        admin_states.pop(ADMIN_ID, None)
        return

    tag = parts[0].strip()
    description = parts[1] if len(parts) > 1 else "Без описания"

    bot_username = bot.get_me().username
    deep_link = f"https://t.me/{bot_username}?start={tag}"

    channel_caption = (
        f"#{tag}\n"
        f"📝 {description}\n\n"
        f"🔗 {deep_link}"
    )

    try:
        sent_msg = bot.copy_message(STORAGE_CHANNEL_ID, message.chat.id, message.message_id, caption=channel_caption)
        
        file_data = {
            "msg_id": sent_msg.message_id,
            "description": description
        }
        save_mapping(tag, file_data)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка публикации в канал (убедись, что бот админ): {e}")
        admin_states.pop(ADMIN_ID, None)
        return

    bot.send_message(
        message.chat.id,
        f"✅ Файл успешно опубликован в канал со всеми данными!\n\n🔗 Ссылка:\n{deep_link}",
        parse_mode=None,
    )
    admin_states.pop(ADMIN_ID, None)

@bot.message_handler(commands=["files"])
def list_files(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
        return

    mapping = load_mapping()
    if not mapping:
        bot.send_message(message.chat.id, "📭 Список файлов пуст.")
        return

    bot_username = bot.get_me().username
    text = "📂 Список сохраненных файлов:\n\n"
    for tag, item in mapping.items():
        link = f"https://t.me/{bot_username}?start={tag}"
        text += f"• Тег: `{tag}`\n  Описание: {item['description']}\n  🔗 {link}\n\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=["del"])
def delete_file(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажи тег для удаления. Пример: `/del gold`", parse_mode="Markdown")
        return

    tag = args[1].strip()
    mapping = load_mapping()

    if tag in mapping:
        # Также пробуем удалить сообщение из самого канала-хранилища для порядка
        try:
            bot.delete_message(STORAGE_CHANNEL_ID, mapping[tag]['msg_id'])
        except Exception:
            pass

        delete_mapping(tag)
        bot.send_message(message.chat.id, f"🗑 Файл с тегом `{tag}` полностью удален из бота и из канала.")
    else:
        bot.send_message(message.chat.id, f"❌ Файл с тегом `{tag}` не найден.")

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

    print("Бот запущен 24/7...")
    bot.infinity_polling()
