import os
from threading import Thread
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

TOKEN = "8847975926:AAGmu4pfRfMa11Ow4hCw0kFURveuFI2YYPw"
CHANNEL_USERNAME = "@goat1488_67"
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1004496422540  # Твой приватный канал для файлов
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("add", "Добавить новый файл"),
    BotCommand("files", "Список всех файлов"),
])

admin_states = {}
files_db = []  # Список для хранения данных в памяти (файлы хранятся в канале навсегда)

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

    if len(args) > 1 and args[1].startswith("get_"):
        try:
            index = int(args[1].replace("get_", ""))
            
            if not check_subscription(user_id):
                markup = InlineKeyboardMarkup()
                channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
                markup.add(InlineKeyboardButton("📢 Подписаться на канал", url=channel_link))
                markup.add(InlineKeyboardButton("✅ Я подписался", callback_data=f"check_sub_{index}"))

                bot.send_message(
                    message.chat.id,
                    "❌ Чтобы получить файл, вы должны быть подписаны на наш канал!",
                    reply_markup=markup,
                )
                return

            if 0 <= index < len(files_db):
                file_item = files_db[index]
                bot.send_document(
                    user_id, 
                    file_item['file_id'], 
                    caption=f"📁 {file_item['name']}"
                )
            else:
                bot.send_message(message.chat.id, "❌ Файл не найден или был удален.")
                
        except ValueError:
            pass
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
    index = int(call.data.split("_")[2])

    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
        bot.delete_message(call.message.chat.id, call.message.message_id)

        if 0 <= index < len(files_db):
            file_item = files_db[index]
            bot.send_document(user_id, file_item['file_id'], caption=f"📁 {file_item['name']}")
    else:
        bot.answer_callback_query(call.id, "❌ Вы все еще не подписаны на канал!", show_alert=True)

@bot.message_handler(commands=["add"])
def add_file_step1(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
        return

    admin_states[ADMIN_ID] = "waiting_for_file"
    bot.send_message(
        message.chat.id,
        "📤 **Отправьте файл**.\nВ описании к файлу (caption) укажи название.\n\n*Пример:* `config have ash hvh`",
        parse_mode="Markdown",
    )

@bot.message_handler(content_types=["document", "photo", "video"], func=lambda m: m.from_user.id == ADMIN_ID)
def handle_incoming_file(message):
    if admin_states.get(ADMIN_ID) != "waiting_for_file":
        return

    file_title = message.caption if message.caption else "Без названия"

    try:
        # Пересылаем в твой приватный канал для вечного хранения
        forwarded_msg = bot.forward_message(STORAGE_CHANNEL_ID, message.chat.id, message.message_id)
        file_id = forwarded_msg.document.file_id if forwarded_msg.document else forwarded_msg.photo[-1].file_id
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения в канал (убедись, что бот админ): {e}")
        admin_states.pop(ADMIN_ID, None)
        return

    files_db.append({"name": file_title, "file_id": file_id})
    new_index = len(files_db) - 1

    bot_username = bot.get_me().username
    deep_link = f"https://t.me/{bot_username}?start=get_{new_index}"

    bot.send_message(
        message.chat.id,
        f"✅ Файл успешно сохранен в канал!\n\n📌 Название: *{file_title}*\n🔗 Ссылка для выдачи:\n{deep_link}",
        parse_mode="Markdown",
    )
    admin_states.pop(ADMIN_ID, None)

@bot.message_handler(commands=["files"])
def list_files(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ У вас нет прав администратора.")
        return

    if not files_db:
        bot.send_message(message.chat.id, "📭 Список файлов пуст.")
        return

    bot_username = bot.get_me().username
    text = "📂 Список сохраненных файлов:\n\n"
    for idx, item in enumerate(files_db):
        link = f"https://t.me/{bot_username}?start=get_{idx}"
        text += f"• *{item['name']}*\n🔗 {link}\n\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

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
