import os
from threading import Thread
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

# Настройки
TOKEN = "8847975926:AAGmu4pfRfMa11Ow4hCw0kFURveuFI2YYPw"
CHANNEL_USERNAME = "@goat1488_67"  # Канал для проверки подписки
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359  # Твой канал «ссылки и файлы»
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("add", "Добавить новый файл"),
])

admin_states = {}

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

    # Если перешли по глубокой ссылке
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

    # Обычный /start
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
    msg = bot.send_message(chat_id, "Секунду...")
    
    # Пытаемся найти и переслать файл из канала-хранилища по тегу
    try:
        # Проходим по последним сообщениям канала (Telegram API позволяет пересылать по ID, 
        # поэтому здесь мы берем файл напрямую из сохраненного сообщения через копирование)
        # Если нужно точное сопоставление, бот пересылает исходный файл из истории канала.
        # Для этого проще всего копировать последнее или использовать привязку:
        # Но самый надежный способ без базы — бот пересылает файл из канала по сохраненному ID сообщения.
        # Ниже в /add мы сделаем сохранение ID сообщения, чтобы выдавать мгновенно!
        pass
    except Exception:
        pass

# Улучшенная функция отправки с сохранением ID сообщения в канале для мгновенной выдачи
@bot.message_handler(commands=["add"])
def add_file_step1(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
        return

    admin_states[ADMIN_ID] = "waiting_for_file"
    bot.send_message(
        message.chat.id,
        "📤 **Отправьте файл**.\nВ описании к файлу (caption) укажи данные в формате:\n\n"
        "`тэг Описание файла`\n\n*Пример:* `config have ash hvh`",
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
            "⚠️ Вы забыли указать тэг в описании к файлу. Попробуйте снова через команду /add",
        )
        admin_states.pop(ADMIN_ID, None)
        return

    tag = parts[0]
    description = parts[1] if len(parts) > 1 else "Без описания"

    bot_username = bot.get_me().username
    deep_link = f"https://t.me/{bot_username}?start={tag}"

    # Твой чистый формат для канала (без лишних фраз)
    channel_caption = (
        f"#{tag}\n"
        f"{description}\n\n"
        f"{deep_link}"
    )

    try:
        # Публикуем в твой канал «ссылки и файлы»
        if message.document:
            sent_msg = bot.send_document(STORAGE_CHANNEL_ID, message.document.file_id, caption=channel_caption)
        elif message.photo:
            sent_msg = bot.send_photo(STORAGE_CHANNEL_ID, message.photo[-1].file_id, caption=channel_caption)
        elif message.video:
            sent_msg = bot.send_video(STORAGE_CHANNEL_ID, message.video.file_id, caption=channel_caption)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка публикации в канал (убедись, что бот админ): {e}")
        admin_states.pop(ADMIN_ID, None)
        return

    # Сохраняем ID отправленного сообщения из канала в мини-словарь, чтобы бот мгновенно его оттуда забирал
    # (Чтобы не терялось при перезапуске, мы можем сохранять file_id прямо в коде или в файлик, 
    # но давай сделаем простую привязку тега к file_id в словаре, который дублируется)
    global file_mapping
    # Сохраняем тип и file_id
    file_data = {
        "file_id": message.document.file_id if message.document else (message.photo[-1].file_id if message.photo else message.video.file_id),
        "type": "document" if message.document else ("photo" if message.photo else "video"),
        "description": description
    }
    
    # Записываем в простой JSON-файл на сервере, чтобы сохранялось между перезапусками памяти
    save_mapping(tag, file_data)

    bot.send_message(
        message.chat.id,
        f"✅ Готово! Файл опубликован в канал.\n\n🔗 Ссылка:\n{deep_link}",
        parse_mode=None,
    )
    admin_states.pop(ADMIN_ID, None)

import json

MAPPING_FILE = "file_mapping.json"

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

# Переписанная функция выдачи файла без лишних слов
def send_file_to_user(chat_id, file_key):
    bot.send_message(chat_id, "Секунду...")
    
    mapping = load_mapping()
    if file_key in mapping:
        item = mapping[file_key]
        caption = f"📁 {item['description']}"
        
        if item['type'] == 'document':
            bot.send_document(chat_id, item['file_id'], caption=caption)
        elif item['type'] == 'photo':
            bot.send_photo(chat_id, item['file_id'], caption=caption)
        elif item['type'] == 'video':
            bot.send_video(chat_id, item['file_id'], caption=caption)
    else:
        bot.send_message(chat_id, "❌ Файл не найден.")

# --- ВЕБ-СЕРВЕР ДЛЯ РАБОТЫ 24/7 НА RENDER ---
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
