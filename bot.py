import json
import os
from threading import Thread
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

TOKEN = "8924359904:AAHU9R3DZ4PjvxxnUvU_Y5_Dh7e13_RECvI"
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("add", "Добавить новый файл"),
    BotCommand("files", "Список всех файлов"),
    BotCommand("del", "Удалить файл по тегу"),
])

admin_states = {}

def load_mapping():
    try:
        chat = bot.get_chat(STORAGE_CHANNEL_ID)
        if chat.pinned_message:
            text = chat.pinned_message.text or ""
            if "CONFIG_MAP:" in text:
                json_str = text.split("CONFIG_MAP:")[1].strip()
                return json.loads(json_str)
    except Exception as e:
        print(f"Ошибка чтения базы из канала: {e}")
    return {}

def save_mapping_data(mapping):
    try:
        json_str = json.dumps(mapping, ensure_ascii=False)
        full_text = f"⚙️ СЛУЖЕБНАЯ БАЗА ДАННЫХ БОТА\nCONFIG_MAP:\n{json_str}"
        msg = bot.send_message(STORAGE_CHANNEL_ID, full_text)
        bot.pin_chat_message(STORAGE_CHANNEL_ID, msg.message_id)
    except Exception as e:
        print(f"Ошибка сохранения базы в канал: {e}")

def save_mapping(tag, data):
    mapping = load_mapping()
    mapping[tag] = data
    save_mapping_data(mapping)

def delete_mapping(tag):
    mapping = load_mapping()
    if tag in mapping:
        del mapping[tag]
        save_mapping_data(mapping)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1:
        file_key = args[1]
        send_file_to_user(message.chat.id, file_key)
        return

    markup = InlineKeyboardMarkup()
    btn_ls = InlineKeyboardButton("👤 Мое ЛС", url=FEEDBACK_BOT_URL)
    markup.add(btn_ls)

    caption_text = "👋 Привет!\n\n👀 Твой личный файловый менеджер"
    try:
        with open("god.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=markup)

def send_file_to_user(chat_id, file_key):
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
        return
    admin_states[ADMIN_ID] = "waiting_for_file"
    bot.send_message(message.chat.id, "📤 Отправь файл, указав тег в описании (например: `hmscore`)", parse_mode="Markdown")

@bot.message_handler(content_types=["document", "photo", "video"], func=lambda m: m.from_user.id == ADMIN_ID)
def handle_incoming_file(message):
    if admin_states.get(ADMIN_ID) != "waiting_for_file":
        return

    text = message.caption or ""
    parts = text.split(maxsplit=1)
    if not parts:
        bot.send_message(message.chat.id, "⚠️ Укажи тег в описании!")
        admin_states.pop(ADMIN_ID, None)
        return

    tag = parts[0].strip()
    bot_username = bot.get_me().username
    deep_link = f"https://t.me/{bot_username}?start={tag}"

    channel_caption = f"#{tag}\n🔗 {deep_link}"

    try:
        sent_msg = bot.copy_message(STORAGE_CHANNEL_ID, message.chat.id, message.message_id, caption=channel_caption)
        file_data = {"msg_id": sent_msg.message_id}
        save_mapping(tag, file_data)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
        admin_states.pop(ADMIN_ID, None)
        return

    bot.send_message(message.chat.id, f"✅ Сохранено:\n{tag} - {deep_link}")
    admin_states.pop(ADMIN_ID, None)

@bot.message_handler(commands=["files"])
def list_files(message):
    if message.from_user.id != ADMIN_ID:
        return

    mapping = load_mapping()
    if not mapping:
        bot.send_message(message.chat.id, "📭 Список пуст.")
        return

    bot_username = bot.get_me().username
    text = ""
    for tag in mapping.keys():
        link = f"https://t.me/{bot_username}?start={tag}"
        text += f"{tag} - {link}\n"

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["del"])
def delete_file(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажи тег: `/del hmscore`", parse_mode="Markdown")
        return

    tag = args[1].strip()
    mapping = load_mapping()

    if tag in mapping:
        try:
            bot.delete_message(STORAGE_CHANNEL_ID, mapping[tag]['msg_id'])
        except Exception:
            pass
        delete_mapping(tag)
        bot.send_message(message.chat.id, f"🗑 Успешно удалено: {tag}")
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
    bot.infinity_polling()
