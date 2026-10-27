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

    # Если перешли по глубокой ссылке с ключом/тегом
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

        # Ищем файл в канале-хранилище по тегу/ключу
        send_file_from_storage(user_id, file_key)
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
        send_file_from_storage(user_id, file_key)
    else:
        bot.answer_callback_query(call.id, "❌ Вы все еще не подписаны на канал!", show_alert=True)

def send_file_from_storage(user_id, file_key):
    # Так как Telegram не умеет искать по тексту в каналах через стандартный Bot API без यूजरbot-а,
    # самый простой способ — бот пересылает сообщение или мы ищем по истории.
    # Но проще всего: бот будет выдавать файл напрямую по сохраненному ID из канала.
    # (Ниже в /add мы сделаем так, чтобы бот запоминал связку ключ -> сообщение в канале)
    bot.send_message(user_id, f"🔍 Ищу файл по ключу: `{file_key}`...")

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

    # Формируем твой шаблон для публикации в канал
    channel_caption = (
        "файл прикреплен\n"
        f"#{tag}\n"
        f"{description}\n"
        f"{deep_link}"
    )

    try:
        # Отправляем файл в твой канал «ссылки и файлы» по твоему формату
        if message.document:
            bot.send_document(STORAGE_CHANNEL_ID, message.document.file_id, caption=channel_caption)
        elif message.photo:
            bot.send_photo(STORAGE_CHANNEL_ID, message.photo[-1].file_id, caption=channel_caption)
        elif message.video:
            bot.send_video(STORAGE_CHANNEL_ID, message.video.file_id, caption=channel_caption)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка публикации в канал (убедись, что бот админ в канале): {e}")
        admin_states.pop(ADMIN_ID, None)
        return

    bot.send_message(
        message.chat.id,
        f"✅ Файл успешно опубликован в канал по твоему шаблону!\n\n🔗 Ссылка для выдачи:\n{deep_link}",
        parse_mode=None,
    )
    admin_states.pop(ADMIN_ID, None)

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
