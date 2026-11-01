import json
import os
import random
import time
import io
import hashlib
from threading import Thread
import requests
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, MenuButtonWebApp, WebAppInfo
from flask import Flask

TOKEN = "8847975926:AAEFDucz8GiAESHV3f49HF4JqCOS9SrrL5k
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"
SITE_URL = "https://popka22867.github.io/Adapter/"
VT_API_KEY = "fa5af0a32f4aa92be1536149bcf01321aaab83104c67ff7e50c37ff5fa64dcc8"

START_TIME = time.time()

bot = telebot.TeleBot(TOKEN)

admin_states = {}
active_processes = {}

def set_bot_menu_button():
    try:
        bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="My site", web_app=WebAppInfo(url=SITE_URL)))
    except Exception as e:
        print(f"Ошибка установки кнопки меню: {e}")

def load_mapping():
    try:
        chat = bot.get_chat(STORAGE_CHANNEL_ID)
        if chat.pinned_message and chat.pinned_message.document:
            if "db.txt" in chat.pinned_message.document.file_name.lower():
                file_info = bot.get_file(chat.pinned_message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                return json.loads(downloaded_file.decode('utf-8'))
        
        messages = bot.get_chat_history(STORAGE_CHANNEL_ID, limit=100)
        for msg in messages:
            if msg.document and msg.document.file_name and "db.txt" in msg.document.file_name.lower():
                file_info = bot.get_file(msg.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                return json.loads(downloaded_file.decode('utf-8'))
    except Exception as e:
        print(f"Не удалось подгрузить базу из канала: {e}")
    return {}

def save_mapping_data(mapping):
    try:
        with open("db.txt", "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)

        old_pinned_msg_id = None
        try:
            chat = bot.get_chat(STORAGE_CHANNEL_ID)
            if chat.pinned_message:
                old_pinned_msg_id = chat.pinned_message.message_id
        except:
            pass

        with open("db.txt", "rb") as f:
            msg = bot.send_document(
                STORAGE_CHANNEL_ID, 
                f, 
                caption="⚙️ ГЛАВНАЯ СЛУЖЕБНАЯ БАЗА ДАННЫХ ФАЙЛОВ"
            )

        bot.pin_chat_message(STORAGE_CHANNEL_ID, msg.message_id)
        if old_pinned_msg_id:
            try:
                bot.delete_message(STORAGE_CHANNEL_ID, old_pinned_msg_id)
            except:
                pass
        
        try:
            messages = bot.get_chat_history(STORAGE_CHANNEL_ID, limit=100)
            for m in messages:
                if m.document and m.document.file_name and "db.txt" in m.document.file_name.lower() and m.message_id != msg.message_id and m.message_id != old_pinned_msg_id:
                    bot.delete_message(STORAGE_CHANNEL_ID, m.message_id)
        except:
            pass

        if os.path.exists("db.txt"):
            os.remove("db.txt")
    except Exception as e:
        print(f"Ошибка сохранения базы в канал: {e}")

def get_settings(mapping):
    if "_settings" not in mapping:
        mapping["_settings"] = {"channels": ["@goat1488_67"]}
    return mapping["_settings"]

def check_user_subscriptions(user_id, mapping):
    settings = get_settings(mapping)
    channels = settings.get("channels", ["@goat1488_67"])
    not_subbed = []
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_subbed.append(ch)
        except Exception as e:
            print(f"Не удалось проверить подписку на {ch}: {e}")
    return not_subbed

def get_sub_keyboard(not_subbed, file_key):
    markup = InlineKeyboardMarkup(row_width=1)
    for ch in not_subbed:
        clean_ch = ch.replace("@", "")
        markup.add(InlineKeyboardButton(f"📢 Подписаться на {ch}", url=f"https://t.me/{clean_ch}"))
    markup.add(InlineKeyboardButton("🔄 Я подписался (-ась)", callback_data=f"sub_check_{file_key}"))
    return markup

def get_start_keyboard(is_admin=False):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_channel = InlineKeyboardButton("📢 Наш канал", url="https://t.me/goat1488_67")
    btn_profile = InlineKeyboardButton("⚙️ Профиль", callback_data="open_profile")
    btn_feedback = InlineKeyboardButton("👤 Обратная связь", url=FEEDBACK_BOT_URL)
    btn_suggest = InlineKeyboardButton("📤 Предложить файл", callback_data="click_suggest")
    btn_commands = InlineKeyboardButton("📋 Команды", callback_data="click_commands")
    
    markup.add(btn_channel, btn_profile)
    markup.add(btn_feedback, btn_suggest, btn_commands)
    return markup

def get_profile_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_back = InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    markup.add(btn_back)
    return markup

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user = message.from_user
    is_admin = (user.id == ADMIN_ID)

    if is_admin:
        try:
            bot.set_my_commands([
                BotCommand("start", "Запустить бота"),
                BotCommand("add", "Добавить файл в базу"),
                BotCommand("edit", "Изменить файл по тегу"),
                BotCommand("files", "Список файлов базы"),
                BotCommand("search", "Поиск файла"),
                BotCommand("del", "Удалить файл по тегу"),
                BotCommand("links", "Каналы подписки"),
                BotCommand("full", "Выгрузить все файлы"),
                BotCommand("stop", "Остановить выгрузку"),
                BotCommand("db", "Скачать главную базу"),
                BotCommand("update_db", "Обновить базу описаний"),
                BotCommand("suggest", "Предложить файл"),
                BotCommand("check_vt", "Проверить через VT"),
                BotCommand("help", "Список доступных команд"),
            ], scope=telebot.types.BotCommandScopeChat(chat_id=ADMIN_ID))
        except Exception:
            pass
    else:
        try:
            bot.set_my_commands([
                BotCommand("start", "Запустить бота"),
                BotCommand("suggest", "Предложить файл"),
                BotCommand("check_vt", "Проверить через VT"),
                BotCommand("help", "Список доступных команд"),
            ], scope=telebot.types.BotCommandScopeChat(chat_id=user.id))
        except Exception:
            pass

    args = message.text.split()
    mapping = load_mapping()

    if len(args) > 1:
        file_key = args[1]
        
        not_subbed = check_user_subscriptions(user.id, mapping)
        if not_subbed:
            bot.send_message(
                message.chat.id,
                "❌ Для получения файла необходимо подписаться на наш канал:",
                reply_markup=get_sub_keyboard(not_subbed, file_key)
            )
            return

        if file_key in mapping:
            if "downloads" not in mapping[file_key]:
                mapping[file_key]["downloads"] = 0
            mapping[file_key]["downloads"] += 1
            
            user_key = f"dl_user_{user.id}"
            if user_key not in mapping[file_key]:
                mapping[file_key][user_key] = 0
            mapping[file_key][user_key] += 1
            
            save_mapping_data(mapping)
            send_file_to_user(message.chat.id, file_key)
        else:
            bot.send_message(message.chat.id, "❌ Файл не найден.")
        return

    caption_text = (
        "👋 Привет!\n\n"
        "💬 Я файловый менеджер и храню файлы с канала @goat1488_67!\n\n"
        "🔽 Используй кнопки ниже для навигации"
    )
    
    try:
        with open("1.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=get_start_keyboard(is_admin))
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=get_start_keyboard(is_admin))

@bot.message_handler(commands=["help"])
def help_cmd(message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    
    if is_admin:
        text = (
            "📋 Доступные команды (Администратор):\n\n"
            "/start — Запустить бота\n"
            "/add — Добавить новый файл в базу\n"
            "/edit [тег] — Изменить файл/описание\n"
            "/del [тег] — Удалить файл из базы\n"
            "/files — Список всех файлов (страницы)\n"
            "/search [запрос] — Поиск файла по тегу/описанию\n"
            "/full — Выгрузить все файлы в ЛС\n"
            "/stop — Остановить выгрузку\n"
            "/db — Скачать главный файл db.txt\n"
            "/update_db — Обновить базу описаний\n"
            "/links — Управление каналами подписки\n"
            "/suggest — Предложить файл\n"
            "/check_vt — Проверить файл через VirusTotal\n"
            "/help — Список команд"
        )
    else:
        text = (
            "📋 Доступные команды:\n\n"
            "/start — Запустить бота\n"
            "/suggest — Предложить файл в базу\n"
            "/check_vt — Проверить файл через VirusTotal\n"
            "/help — Список команд"
        )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["db"])
def send_database_txt(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        chat = bot.get_chat(STORAGE_CHANNEL_ID)
        if chat.pinned_message and chat.pinned_message.document and "db.txt" in chat.pinned_message.document.file_name.lower():
            bot.send_document(message.chat.id, chat.pinned_message.document.file_id)
            return
        
        messages = bot.get_chat_history(STORAGE_CHANNEL_ID, limit=50)
        for msg in messages:
            if msg.document and msg.document.file_name and "db.txt" in msg.document.file_name.lower():
                bot.send_document(message.chat.id, msg.document.file_id)
                return
        bot.send_message(message.chat.id, "❌ Файл db.txt не найден в канале.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=["suggest"])
def suggest_cmd(message):
    user_id = message.from_user.id
    admin_states[user_id] = {"action": "suggest_file"}
    bot.send_message(message.chat.id, "📤 Отправьте файл, фото или видео с тегом и описанием в подписи (например: my_tag Описание файла)")

@bot.message_handler(commands=["check_vt"])
def check_vt_cmd(message):
    user_id = message.from_user.id
    admin_states[user_id] = {"action": "check_vt_file"}
    bot.send_message(message.chat.id, "🛡 Отправьте файл для проверки через VirusTotal (весом до 20 МБ):")

@bot.message_handler(commands=["update_db"])
def update_database_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    mapping = load_mapping()
    updated_count = 0
    
    for tag, data in mapping.items():
        if tag == "_settings":
            continue
        msg_id = data.get("msg_id")
        if msg_id:
            try:
                msg = bot.forward_message(ADMIN_ID, STORAGE_CHANNEL_ID, msg_id)
                caption = msg.caption or ""
                bot.delete_message(ADMIN_ID, msg.message_id)
                
                if caption:
                    lines = caption.split("\n")
                    desc_lines = []
                    for line in lines:
                        if line.startswith("#") or line.startswith("🔗"):
                            continue
                        desc_lines.append(line)
                    clean_desc = "\n".join(desc_lines).strip()
                    
                    if clean_desc and data.get("desc", "") != clean_desc:
                        data["desc"] = clean_desc
                        updated_count += 1
            except Exception as e:
                print(f"Ошибка проверки сообщения {msg_id} для тега {tag}: {e}")
                
    save_mapping_data(mapping)
    bot.send_message(message.chat.id, f"✅ База данных успешно обновлена! Проверено и подтянуто описаний: {updated_count}")

def get_files_page_keyboard(page, total_pages, search_query=""):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"files_page_{page-1}_{search_query}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"files_page_{page+1}_{search_query}"))
        
    if buttons:
        markup.add(*buttons)
    return markup

def show_files_page(chat_id, message_id, page=1, search_query=""):
    mapping = load_mapping()
    files_only = {k: v for k, v in mapping.items() if k != "_settings"}

    if search_query:
        files_only = {k: v for k, v in files_only.items() if search_query.lower() in k.lower() or search_query.lower() in v.get("desc", "").lower()}

    if not files_only:
        text = "📭 Список файлов пуст или ничего не найдено."
        try:
            bot.edit_message_text(text, chat_id, message_id)
        except:
            bot.send_message(chat_id, text)
        return

    items_per_page = 3
    keys = list(files_only.keys())
    total_items = len(keys)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if page < 1: page = 1
    if page > total_pages: page = total_pages
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_keys = keys[start_idx:end_idx]

    bot_username = bot.get_me().username
    text = f"📂 Список файлов (Страница {page} из {total_pages}):\n\n"
    
    for tag in current_keys:
        data = files_only[tag]
        link = f"https://t.me/{bot_username}?start={tag}"
        desc = data.get("desc", "")
        downloads = data.get("downloads", 0)
        text += f"🔗 {link}\n"
        if desc:
            text += f"📝 Описание: {desc}\n"
        text += f"📥 Скачиваний: {downloads}\n\n"

    markup = get_files_page_keyboard(page, total_pages, search_query)
    
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, disable_web_page_preview=True)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup, disable_web_page_preview=True)

@bot.message_handler(commands=["files"])
def list_files_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    show_files_page(message.chat.id, message.message_id, page=1)

@bot.message_handler(commands=["search"])
def search_file_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажи текст для поиска (тег или описание): /search твой_запрос")
        return
    query = args[1].strip()
    
    mapping = load_mapping()
    files_only = {k: v for k, v in mapping.items() if k != "_settings"}
    
    found = {}
    for tag, data in files_only.items():
        desc = data.get("desc", "")
        if query.lower() in tag.lower() or query.lower() in desc.lower():
            found[tag] = data

    if not found:
        bot.send_message(message.chat.id, "❌ Ничего не найдено по вашему запросу.")
        return

    bot_username = bot.get_me().username
    text = f"🔍 Результаты поиска по запросу '{query}':\n\n"
    for tag, data in found.items():
        link = f"https://t.me/{bot_username}?start={tag}"
        desc = data.get("desc", "")
        downloads = data.get("downloads", 0)
        text += f"🔗 {link}\n"
        if desc:
            text += f"📝 Описание: {desc}\n"
        text += f"📥 Скачиваний: {downloads}\n\n"

    bot.send_message(message.chat.id, text, disable_web_page_preview=True)

@bot.message_handler(commands=["stop"])
def stop_process_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    active_processes[ADMIN_ID] = False
    bot.send_message(message.chat.id, "🛑 Процесс выгрузки успешно отменен.")

@bot.message_handler(commands=["full"])
def full_backup_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    
    mapping = load_mapping()
    files_only = {k: v for k, v in mapping.items() if k != "_settings"}
    
    if not files_only:
        bot.send_message(message.chat.id, "📭 База данных пуста, файлов нет.")
        return
    
    active_processes[ADMIN_ID] = True
    bot.send_message(message.chat.id, f"📦 Начинаю выгрузку всех файлов ({len(files_only)} шт.)...\nНапиши /stop для отмены")
    
    for tag, data in files_only.items():
        if not active_processes.get(ADMIN_ID, True):
            bot.send_message(message.chat.id, "🛑 Выгрузка прервана.")
            return
        try:
            bot.copy_message(message.chat.id, STORAGE_CHANNEL_ID, data.get("msg_id"))
            time.sleep(0.3)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка выгрузки тега {tag}: {e}")
            
    if active_processes.get(ADMIN_ID, True):
        bot.send_message(message.chat.id, "✅ Выгрузка всех файлов завершена!")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "click_suggest":
        admin_states[user.id] = {"action": "suggest_file"}
        bot.send_message(chat_id, "📤 Отправьте файл, фото или видео с тегом и описанием в подписи (например: my_tag Описание файла)")
        bot.answer_callback_query(call.id)

    elif call.data == "click_commands":
        is_admin = (user.id == ADMIN_ID)
        if is_admin:
            text = (
                "📋 Доступные команды (Администратор):\n\n"
                "/start — Запустить бота\n"
                "/add — Добавить новый файл в базу\n"
                "/edit [тег] — Изменить файл/описание\n"
                "/del [тег] — Удалить файл из базы\n"
                "/files — Список всех файлов (страницы)\n"
                "/search [запрос] — Поиск файла по тегу/описанию\n"
                "/full — Выгрузить все файлы в ЛС\n"
                "/stop — Остановить выгрузку\n"
                "/db — Скачать главный файл db.txt\n"
                "/update_db — Обновить базу описаний\n"
                "/links — Управление каналами подписки\n"
                "/suggest — Предложить файл\n"
                "/check_vt — Проверить файл через VirusTotal\n"
                "/help — Список команд"
            )
        else:
            text = (
                "📋 Доступные команды:\n\n"
                "/start — Запустить бота\n"
                "/suggest — Предложить файл в базу\n"
                "/check_vt — Проверить файл через VirusTotal\n"
                "/help — Список команд"
            )
        bot.send_message(chat_id, text)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("approve_suggest_"):
        parts = call.data.split("_")
        target_user_id = int(parts[2])
        caption = call.message.caption or ""
        lines = caption.split("\n")
        tag = lines[0].replace("#", "").strip() if lines else "file"
        user_description = "\n".join(lines[1:-2]).strip() if len(lines) > 3 else ""

        bot_username = bot.get_me().username
        deep_link = f"https://t.me/{bot_username}?start={tag}"
        channel_caption = f"#{tag}\n\n{user_description}\n\n🔗 {deep_link}"

        try:
            if call.message.photo:
                sent_msg = bot.send_photo(STORAGE_CHANNEL_ID, call.message.photo[-1].file_id, caption=channel_caption)
            elif call.message.document:
                sent_msg = bot.send_document(STORAGE_CHANNEL_ID, call.message.document.file_id, caption=channel_caption)
            elif call.message.video:
                sent_msg = bot.send_video(STORAGE_CHANNEL_ID, call.message.video.file_id, caption=channel_caption)
            else:
                sent_msg = bot.copy_message(STORAGE_CHANNEL_ID, chat_id, call.message.message_id, caption=channel_caption)

            mapping = load_mapping()
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0, "desc": user_description}
            save_mapping_data(mapping)

            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f"{caption}\n\n✅ ОДОБРЕНО")
            bot.send_message(target_user_id, "✅ Администрация одобрила ваш файл!")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка при одобрении: {e}")
        bot.answer_callback_query(call.id, "Файл успешно одобрен и добавлен!")

    elif call.data.startswith("reject_suggest_"):
        parts = call.data.split("_")
        target_user_id = int(parts[2])
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f"{call.message.caption}\n\n❌ ОТКЛОНЕНО")
            bot.send_message(target_user_id, "❌ Администрация отклонила ваш файл.")
        except:
            pass
        bot.answer_callback_query(call.id, "Заявка отклонена.")

    elif call.data.startswith("edit_approve_suggest_"):
        parts = call.data.split("_")
        target_user_id = int(parts[3])
        admin_states[ADMIN_ID] = {
            "action": "edit_approve_save",
            "target_user_id": target_user_id,
            "message_id": message_id,
            "original_message": call.message
        }
        bot.send_message(ADMIN_ID, "✏️ Введите новый тег и описание через пробел для одобрения (например: new_tag Новое описание):")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("edit_reject_suggest_"):
        parts = call.data.split("_")
        target_user_id = int(parts[3])
        admin_states[ADMIN_ID] = {
            "action": "edit_reject_save",
            "target_user_id": target_user_id,
            "message_id": message_id,
            "original_message": call.message
        }
        bot.send_message(ADMIN_ID, "💬 Введите причину отклонения (например: Этот файл уже был добавлен или Этот файл содержит вирусы):")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("files_page_"):
        parts = call.data.split("_")
        page = int(parts[2])
        query = "_".join(parts[3:]) if len(parts) > 3 else ""
        show_files_page(chat_id, message_id, page=page, search_query=query)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("sub_check_"):
        file_key = call.data.replace("sub_check_", "")
        mapping = load_mapping()
        not_subbed = check_user_subscriptions(user.id, mapping)
        
        if not_subbed:
            bot.answer_callback_query(call.id, "❌ Вы подписались еще не на все каналы!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            
            if file_key in mapping:
                if "downloads" not in mapping[file_key]:
                    mapping[file_key]["downloads"] = 0
                mapping[file_key]["downloads"] += 1
                
                user_key = f"dl_user_{user.id}"
                if user_key not in mapping[file_key]:
                    mapping[file_key][user_key] = 0
                mapping[file_key][user_key] += 1
                
                save_mapping_data(mapping)
                send_file_to_user(chat_id, file_key)
            else:
                bot.send_message(chat_id, "❌ Файл не найден.")

    elif call.data == "open_profile":
        first_name = user.first_name
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        
        uptime_seconds = int(time.time() - START_TIME)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime_str = f"{days}д {hours}ч {minutes}м" if days > 0 else f"{hours}ч {minutes}м"

        mapping = load_mapping()
        user_key = f"dl_user_{user_id}"
        my_downloads = sum(item.get(user_key, 0) for key, item in mapping.items() if key != "_settings")
        total_downloads = sum(item.get("downloads", 0) for key, item in mapping.items() if key != "_settings")

        profile_caption = (
            f"👤 Профиль\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {first_name}\n"
            f"👤 Username: {username}\n"
            f"⏳ Время работы бота: {uptime_str}\n"
            f"📥 Твоих скачиваний: {my_downloads}\n"
            f"📥 Всего скачиваний в боте: {total_downloads}"
        )
        
        try:
            with open("2.jpg", "rb") as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo.read(), caption=profile_caption),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard()
                )
        except Exception:
            try:
                bot.edit_message_caption(
                    caption=profile_caption,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard()
                )
            except Exception:
                bot.edit_message_text(
                    text=profile_caption,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard()
                )
        bot.answer_callback_query(call.id)

    elif call.data == "back_to_main":
        caption_text = (
            "👋 Привет!\n\n"
            "💬 Я файловый менеджер и храню файлы с канала @goat1488_67!\n\n"
            "🔽 Используй кнопки ниже для навигации"
        )
        is_admin = (user.id == ADMIN_ID)
        try:
            with open("1.png", "rb") as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo.read(), caption=caption_text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard(is_admin)
                )
        except Exception:
            try:
                bot.edit_message_caption(
                    caption=caption_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard(is_admin)
                )
            except Exception:
                bot.edit_message_text(
                    text=caption_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard(is_admin)
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
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    admin_states[ADMIN_ID] = {"action": "add"}
    bot.send_message(
        message.chat.id, 
        "📤 Отправь файл/картинку с тегом и описанием в подписи (например: ttrgreentrust Текст описания)"
    )

@bot.message_handler(commands=["edit"])
def edit_file_step1(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажи тег для редактирования: /edit ttrgreentrust")
        return
    
    tag = args[1].strip()
    mapping = load_mapping()
    if tag not in mapping:
        bot.send_message(message.chat.id, f"❌ Файл с тегом {tag} не найден в базе.")
        return

    admin_states[ADMIN_ID] = {"action": "edit", "tag": tag}
    bot.send_message(
        message.chat.id, 
        f"✏️ Отправь новый файл/картинку и текст для тега {tag} (пост в канале обновится автоматически)"
    )

@bot.message_handler(commands=["del"])
def delete_file(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажи тег: /del hmscore")
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
        bot.send_message(message.chat.id, f"❌ Файл с тегом {tag} не найден.")

@bot.message_handler(commands=["links"])
def manage_links(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
        return
    args = message.text.split(maxsplit=2)
    mapping = load_mapping()
    settings = get_settings(mapping)
    channels = settings.get("channels", ["@goat1488_67"])

    if len(args) < 2:
        text = "🔗 Текущие каналы для проверки подписки:\n\n"
        for ch in channels:
            text += f"• {ch}\n"
        text += (
            "\n⚙️ Управление:\n"
            "• Добавить: /links add @channel\n"
            "• Удалить: /links del @channel"
        )
        bot.send_message(message.chat.id, text)
        return

    action = args[1].lower()
    if len(args) < 3:
        bot.send_message(message.chat.id, "⚠️ Укажи юзернейм канала, например: /links add @goat1488_67")
        return

    channel_target = args[2].strip()
    if not channel_target.startswith("@"):
        channel_target = "@" + channel_target

    if action == "add":
        if channel_target not in channels:
            channels.append(channel_target)
            settings["channels"] = channels
            save_mapping_data(mapping)
            bot.send_message(message.chat.id, f"✅ Канал {channel_target} успешно добавлен в проверку подписки!")
        else:
            bot.send_message(message.chat.id, f"⚠️ Канал {channel_target} уже есть в списке.")
    elif action == "del":
        if channel_target in channels:
            if len(channels) <= 1:
                bot.send_message(message.chat.id, "❌ Нельзя удалить последний канал! Должен оставаться хотя бы один.")
                return
            channels.remove(channel_target)
            settings["channels"] = channels
            save_mapping_data(mapping)
            bot.send_message(message.chat.id, f"🗑 Канал {channel_target} удален из проверки подписки.")
        else:
            bot.send_message(message.chat.id, f"❌ Канал {channel_target} не найден в списке.")

@bot.message_handler(content_types=["document", "photo", "video", "text"])
def handle_incoming_file(message):
    user_id = message.from_user.id
    state = admin_states.get(user_id, {})
    action = state.get("action")
    
    if not action:
        return

    text = message.caption or message.text or ""

    if action == "edit_approve_save":
        target_user_id = state.get("target_user_id")
        orig_msg = state.get("original_message")
        msg_id_to_edit = state.get("message_id")

        parts = text.split(maxsplit=1)
        if not parts:
            bot.send_message(message.chat.id, "⚠️ Введите новый тег и описание!")
            return

        tag = parts[0].strip()
        user_description = parts[1] if len(parts) > 1 else ""
        bot_username = bot.get_me().username
        deep_link = f"https://t.me/{bot_username}?start={tag}"
        channel_caption = f"#{tag}\n\n{user_description}\n\n🔗 {deep_link}"

        try:
            if orig_msg.photo:
                sent_msg = bot.send_photo(STORAGE_CHANNEL_ID, orig_msg.photo[-1].file_id, caption=channel_caption)
            elif orig_msg.document:
                sent_msg = bot.send_document(STORAGE_CHANNEL_ID, orig_msg.document.file_id, caption=channel_caption)
            elif orig_msg.video:
                sent_msg = bot.send_video(STORAGE_CHANNEL_ID, orig_msg.video.file_id, caption=channel_caption)
            else:
                sent_msg = bot.copy_message(STORAGE_CHANNEL_ID, ADMIN_ID, orig_msg.message_id, caption=channel_caption)

            mapping = load_mapping()
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0, "desc": user_description}
            save_mapping_data(mapping)

            bot.edit_message_caption(chat_id=ADMIN_ID, message_id=msg_id_to_edit, caption=f"{orig_msg.caption}\n\n✅ ОДОБРЕНО И ИЗМЕНЕНО")
            bot.send_message(target_user_id, f"✅ Администрация одобрила и добавила ваш файл по ссылке: {deep_link}")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

        admin_states.pop(user_id, None)
        return

    elif action == "edit_reject_save":
        target_user_id = state.get("target_user_id")
        orig_msg = state.get("original_message")
        msg_id_to_edit = state.get("message_id")
        reason = text.strip()

        try:
            bot.edit_message_caption(chat_id=ADMIN_ID, message_id=msg_id_to_edit, caption=f"{orig_msg.caption}\n\n❌ ОТКЛОНЕНО: {reason}")
            bot.send_message(target_user_id, f"❌ Администрация отклонила ваш файл.\nПричина: {reason}")
            bot.send_message(ADMIN_ID, "✅ Уведомление об отклонении с причиной отправлено пользователю.")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

        admin_states.pop(user_id, None)
        return

    elif action == "suggest_file":
        parts = text.split(maxsplit=1)
        if not parts:
            bot.send_message(message.chat.id, "⚠️ Укажите тег в описании!")
            admin_states.pop(user_id, None)
            return

        tag = parts[0].strip()
        user_description = parts[1] if len(parts) > 1 else ""
        user_name = message.from_user.first_name
        
        forward_caption = f"#{tag}\n\n{user_description}\n\nПредложил: {user_name}"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_suggest_{user_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_suggest_{user_id}"),
            InlineKeyboardButton("✏️ Одобрить и изменить", callback_data=f"edit_approve_suggest_{user_id}"),
            InlineKeyboardButton("✏️ Отклонить и изменить", callback_data=f"edit_reject_suggest_{user_id}")
        )

        try:
            if message.content_type == "photo":
                bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=forward_caption, reply_markup=markup)
            elif message.content_type == "document":
                bot.send_document(ADMIN_ID, message.document.file_id, caption=forward_caption, reply_markup=markup)
            elif message.content_type == "video":
                bot.send_video(ADMIN_ID, message.video.file_id, caption=forward_caption, reply_markup=markup)
            else:
                bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, caption=forward_caption, reply_markup=markup)

            bot.send_message(message.chat.id, "✅ Ваш файл успешно отправлен администратору на рассмотрение!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка отправки: {e}")

        admin_states.pop(user_id, None)
        return

    elif action == "check_vt_file":
        if not VT_API_KEY:
            bot.send_message(message.chat.id, "⚠️ Интеграция с VirusTotal не настроена.")
            admin_states.pop(user_id, None)
            return
            
        bot.send_message(message.chat.id, "🛡 Отправляем файл на проверку в VirusTotal, подождите...")
        try:
            file_info = bot.get_file(message.document.file_id if message.document else message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            files = {'file': (message.document.file_name if message.document else "file.bin", downloaded_file)}
            headers = {'x-apikey': VT_API_KEY}
            
            response = requests.post('https://www.virustotal.com/api/v3/files', files=files, headers=headers, timeout=15)
            
            file_hash = hashlib.sha256(downloaded_file).hexdigest()
            report_url = f"https://www.virustotal.com/gui/file/{file_hash}"
            
            if response.status_code == 200:
                bot.send_message(message.chat.id, f"✅ Файл успешно отправлен на проверку!\n\n🔗 Отчет VirusTotal: {report_url}")
            else:
                err_data = response.json()
                err_code = err_data.get("error", {}).get("code", "")
                if err_code == "AlreadySubmittedError":
                    bot.send_message(message.chat.id, f"ℹ️ Этот файл уже есть в базе VirusTotal!\n\n🔗 Отчет: {report_url}")
                else:
                    bot.send_message(message.chat.id, f"❌ Ошибка загрузки в VirusTotal: {response.text}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Произошла ошибка при проверке: {e}")
            
        admin_states.pop(user_id, None)
        return

    if user_id != ADMIN_ID:
        return

    action = state.get("action")
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
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0, "desc": user_description}
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

                mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": downloads_count, "desc": user_description}
                save_mapping_data(mapping)

                bot.send_message(message.chat.id, f"✏️ Файл с тегом {tag} успешно обновлен!")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ошибка при обновлении: {e}")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка: тег не найден в базе.")

    admin_states.pop(user_id, None)

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
