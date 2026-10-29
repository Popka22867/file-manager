import json
import os
import random
from threading import Thread
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, MenuButtonWebApp, WebAppInfo
from flask import Flask

TOKEN = "8847975926:AAHhCaIevTIPpwJcDxyHe3BdDKcNZ-1QyUs"
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"
SITE_URL = "https://popka22867.github.io/Adapter/"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота"),
    BotCommand("add", "Добавить новый файл"),
    BotCommand("edit", "Изменить файл/описание по тегу"),
    BotCommand("files", "Список файлов и статистика"),
    BotCommand("del", "Удалить файл по тегу"),
])

admin_states = {}

def set_bot_menu_button():
    try:
        bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="My site", web_app=WebAppInfo(url=SITE_URL)))
    except Exception as e:
        print(f"Ошибка установки кнопки меню: {e}")

def load_mapping():
    try:
        chat = bot.get_chat(STORAGE_CHANNEL_ID)
        if chat.pinned_message and chat.pinned_message.document:
            file_info = bot.get_file(chat.pinned_message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            return json.loads(downloaded_file.decode('utf-8'))
    except Exception as e:
        print(f"База в канале не найдена, проверяем локальный файл: {e}")
    
    if os.path.exists("database.txt"):
        try:
            with open("database.txt", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_mapping_data(mapping):
    try:
        with open("database.txt", "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)

        old_pinned_msg_id = None
        try:
            chat = bot.get_chat(STORAGE_CHANNEL_ID)
            if chat.pinned_message:
                old_pinned_msg_id = chat.pinned_message.message_id
        except:
            pass

        with open("database.txt", "rb") as f:
            msg = bot.send_document(
                STORAGE_CHANNEL_ID, 
                f, 
                caption="⚙️ СЛУЖЕБНАЯ БАЗА ДАННЫХ БОТА"
            )

        bot.pin_chat_message(STORAGE_CHANNEL_ID, msg.message_id)

        if old_pinned_msg_id:
            try:
                bot.delete_message(STORAGE_CHANNEL_ID, old_pinned_msg_id)
            except:
                pass

    except Exception as e:
        print(f"Ошибка сохранения базы в канал: {e}")

def get_start_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_channel = InlineKeyboardButton("📢 Наш канал", url="https://t.me/goat1488_67")
    btn_profile = InlineKeyboardButton("⚙️ Профиль", callback_data="open_profile")
    btn_feedback = InlineKeyboardButton("👤 Обратная связь", url=FEEDBACK_BOT_URL)
    
    markup.add(btn_channel, btn_profile)
    markup.add(btn_feedback)
    return markup

def get_profile_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_back = InlineKeyboardButton("🔙 Назад к файлам", callback_data="back_to_main")
    markup.add(btn_back)
    return markup

@bot.message_handler(commands=["start"])
def send_welcome(message):
    args = message.text.split()
    if len(args) > 1:
        file_key = args[1]
        
        mapping = load_mapping()
        if file_key in mapping:
            if "downloads" not in mapping[file_key]:
                mapping[file_key]["downloads"] = 0
            mapping[file_key]["downloads"] += 1
            save_mapping_data(mapping)
            
            send_file_to_user(message.chat.id, file_key)
        else:
            bot.send_message(message.chat.id, "❌ Файл не найден.")
        return

    caption_text = (
        "👋 Привет!\n\n"
        "💬 Я храню файлы с канала @goat1488_67!\n\n"
        "🔽 Используй кнопки ниже для навигации"
    )
    
    try:
        with open("1.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=get_start_keyboard())
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=get_start_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "open_profile":
        first_name = user.first_name
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        
        mapping = load_mapping()
        total_downloads = sum(item.get("downloads", 0) for item in mapping.values())

        profile_caption = (
            f"👤 Профиль\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Имя: {first_name}\n"
            f"👤 Username: {username}\n"
            f"📥 Всего скачиваний в боте: {total_downloads}"
        )
        
        try:
            with open("2.jpg", "rb") as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo.read(), caption=profile_caption, parse_mode="Markdown"),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard()
                )
        except Exception:
            bot.edit_message_caption(
                caption=profile_caption,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=get_profile_keyboard(),
                parse_mode="Markdown"
            )
        bot.answer_callback_query(call.id)

    elif call.data == "back_to_main":
        caption_text = (
            "👋 Привет!\n\n"
            "💬 Я храню файлы с канала @goat1488_67!\n\n"
            "🔽 Используй кнопки ниже для навигации"
        )
        try:
            with open("1.png", "rb") as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo.read(), caption=caption_text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard()
                )
        except Exception:
            bot.edit_message_caption(
                caption=caption_text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=get_start_keyboard()
            )
        bot.answer_callback_query(call.id)

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
    admin_states[ADMIN_ID] = {"action": "add"}
    bot.send_message(
        message.chat.id, 
        "📤 Отправь файл/картинку с тегом и описанием в подписи (например: `ttrgreentrust Текст описания`)", 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["edit"])
def edit_file_step1(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажи тег для редактирования: `/edit ttrgreentrust`", parse_mode="Markdown")
        return
    
    tag = args[1].strip()
    mapping = load_mapping()
    if tag not in mapping:
        bot.send_message(message.chat.id, f"❌ Файл с тегом `{tag}` не найден в базе.")
        return

    admin_states[ADMIN_ID] = {"action": "edit", "tag": tag}
    bot.send_message(
        message.chat.id, 
        f"✏️ Отправь **новый файл/картинку и текст** для тега `{tag}` (пост в канале обновится автоматически)", 
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=["document", "photo", "video"], func=lambda m: m.from_user.id == ADMIN_ID)
def handle_incoming_file(message):
    state = admin_states.get(ADMIN_ID)
    if not state:
        return

    action = state.get("action")
    text = message.caption or ""
    parts = text.split(maxsplit=1)

    if action == "add":
        if not parts:
            bot.send_message(message.chat.id, "⚠️ Укажи тег в описании!")
            admin_states.pop(ADMIN_ID, None)
            return

        tag = parts[0].strip()
        user_description = parts[1] if len(parts) > 1 else ""
        bot_username = bot.get_me().username
        deep_link = f"https://t.me/{bot_username}?start={tag}"

        channel_caption = f"#{tag}\n\n{user_description}\n\n🔗 {deep_link}"

        try:
            if message.content_type == "photo":
                sent_msg = bot.send_photo(STORAGE_CHANNEL_ID, message.photo[-1].file_id, caption=channel_caption)
            elif message.content_type == "document":
                sent_msg = bot.send_document(STORAGE_CHANNEL_ID, message.document.file_id, caption=channel_caption)
            elif message.content_type == "video":
                sent_msg = bot.send_video(STORAGE_CHANNEL_ID, message.video.file_id, caption=channel_caption)
            else:
                sent_msg = bot.copy_message(STORAGE_CHANNEL_ID, message.chat.id, message.message_id, caption=channel_caption)

            mapping = load_mapping()
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0}
            save_mapping_data(mapping)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
            admin_states.pop(ADMIN_ID, None)
            return

        bot.send_message(message.chat.id, f"✅ Успешно сохранено!\n{tag} - {deep_link}")

    elif action == "edit":
        tag = state.get("tag")
        user_description = text if text else ""
        bot_username = bot.get_me().username
        deep_link = f"https://t.me/{bot_username}?start={tag}"

        channel_caption = f"#{tag}\n\n{user_description}\n\n🔗 {deep_link}"

        mapping = load_mapping()
        if tag in mapping:
            old_msg_id = mapping[tag]["msg_id"]
            downloads_count = mapping[tag].get("downloads", 0)

            try:
                bot.delete_message(STORAGE_CHANNEL_ID, old_msg_id)
            except:
                pass

            try:
                if message.content_type == "photo":
                    sent_msg = bot.send_photo(STORAGE_CHANNEL_ID, message.photo[-1].file_id, caption=channel_caption)
                elif message.content_type == "document":
                    sent_msg = bot.send_document(STORAGE_CHANNEL_ID, message.document.file_id, caption=channel_caption)
                elif message.content_type == "video":
                    sent_msg = bot.send_video(STORAGE_CHANNEL_ID, message.video.file_id, caption=channel_caption)
                else:
                    sent_msg = bot.copy_message(STORAGE_CHANNEL_ID, message.chat.id, message.message_id, caption=channel_caption)

                mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": downloads_count}
                save_mapping_data(mapping)

                bot.send_message(message.chat.id, f"✏️ Файл с тегом `{tag}` успешно обновлен!", parse_mode="Markdown")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ошибка при обновлении: {e}")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка: тег не найден в базе.")

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
    text = "📂 **Список файлов и скачивания:**\n\n"
    for tag, data in mapping.items():
        link = f"https://t.me/{bot_username}?start={tag}"
        downloads = data.get("downloads", 0)
        text += f"{tag} - {link} 📥 [{downloads}]\n"

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
        
        del mapping[tag]
        save_mapping_data(mapping)
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
    set_bot_menu_button()
    t = Thread(target=run_web)
    t.start()
    bot.infinity_polling()
