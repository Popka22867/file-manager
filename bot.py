import json
import os
import random
import time
from threading import Thread
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, MenuButtonWebApp, WebAppInfo
from flask import Flask

TOKEN = "8847975926:AAHE3O0XmmxSpX9UucUds5UkHvfQ6sbwWtA"
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"
SITE_URL = "https://popka22867.github.io/Adapter/"

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("start", "Запустить бота")
], scope=telebot.types.BotCommandScopeDefault())

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
            if "database" in chat.pinned_message.document.file_name.lower():
                file_info = bot.get_file(chat.pinned_message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                return json.loads(downloaded_file.decode('utf-8'))
        
        messages = bot.get_chat_history(STORAGE_CHANNEL_ID, limit=50)
        for msg in messages:
            if msg.document and "database" in msg.document.file_name.lower():
                file_info = bot.get_file(msg.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                return json.loads(downloaded_file.decode('utf-8'))
    except Exception as e:
        print(f"Не удалось подгрузить базу файлов из канала: {e}")
    return {}

def save_mapping_data(mapping):
    try:
        temp_filename = "database.txt"
        with open(temp_filename, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)

        old_pinned_msg_id = None
        try:
            chat = bot.get_chat(STORAGE_CHANNEL_ID)
            if chat.pinned_message:
                old_pinned_msg_id = chat.pinned_message.message_id
        except:
            pass

        with open(temp_filename, "rb") as f:
            msg = bot.send_document(
                STORAGE_CHANNEL_ID, 
                f, 
                caption="⚙️ СЛУЖЕБНАЯ БАЗА ДАННЫХ ФАЙЛОВ"
            )

        bot.pin_chat_message(STORAGE_CHANNEL_ID, msg.message_id)

        if old_pinned_msg_id:
            try:
                bot.delete_message(STORAGE_CHANNEL_ID, old_pinned_msg_id)
            except:
                pass
        
        try:
            messages = bot.get_chat_history(STORAGE_CHANNEL_ID, limit=50)
            for m in messages:
                if m.document and "database" in m.document.file_name.lower() and m.message_id != msg.message_id and m.message_id != old_pinned_msg_id:
                    bot.delete_message(STORAGE_CHANNEL_ID, m.message_id)
        except:
            pass

        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    except Exception as e:
        print(f"Ошибка сохранения базы файлов в канал: {e}")

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
    btn_back = InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    markup.add(btn_back)
    return markup

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user = message.from_user
    
    if user.id == ADMIN_ID:
        try:
            bot.set_my_commands([
                BotCommand("start", "Запустить бота"),
                BotCommand("add", "Добавить новый файл"),
                BotCommand("edit", "Изменить файл/описание по тегу"),
                BotCommand("files", "Список файлов (страницы)"),
                BotCommand("search", "Поиск файла по тегу или описанию"),
                BotCommand("del", "Удалить файл по тегу"),
                BotCommand("links", "Управление каналами подписки"),
                BotCommand("full", "Выгрузить все файлы из базы в ЛС"),
                BotCommand("stop", "Остановить текущую выгрузку /full"),
                BotCommand("database", "Скачать базу файлов"),
                BotCommand("update_database", "Обновить базу и подтянуть описания"),
            ], scope=telebot.types.BotCommandScopeChat(chat_id=ADMIN_ID))
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
                "❌ **Для получения файла необходимо подписаться на наш канал:**",
                reply_markup=get_sub_keyboard(not_subbed, file_key),
                parse_mode="Markdown"
            )
            return

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
        "💬 Я файловый менеджер и храню файлы с канала @goat1488_67!\n\n"
        "🔽 Используй кнопки ниже для навигации"
    )
    
    try:
        with open("1.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=get_start_keyboard())
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=get_start_keyboard())

@bot.message_handler(commands=["database"])
def send_database_txt(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        chat = bot.get_chat(STORAGE_CHANNEL_ID)
        if chat.pinned_message and chat.pinned_message.document and "database" in chat.pinned_message.document.file_name.lower():
            bot.send_document(message.chat.id, chat.pinned_message.document.file_id)
            return
        
        messages = bot.get_chat_history(STORAGE_CHANNEL_ID, limit=50)
        for msg in messages:
            if msg.document and "database" in msg.document.file_name.lower():
                bot.send_document(message.chat.id, msg.document.file_id)
                return
        bot.send_message(message.chat.id, "❌ Файл database.txt не найден в канале.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=["update_database"])
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
            bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, text, parse_mode="Markdown")
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
    text = f"📂 **Список файлов (Страница {page} из {total_pages}):**\n\n"
    
    for tag in current_keys:
        data = files_only[tag]
        link = f"https://t.me/{bot_username}?start={tag}"
        downloads = data.get("downloads", 0)
        text += f"🔗 {link}\n📥 Скачиваний: {downloads}\n\n"

    markup = get_files_page_keyboard(page, total_pages, search_query)
    
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)

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
        bot.send_message(message.chat.id, "⚠️ Укажи текст для поиска (тег или описание): `/search твой_запрос`", parse_mode="Markdown")
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
    text = f"🔍 **Результаты поиска по запросу `{query}`:**\n\n"
    for tag, data in found.items():
        link = f"https://t.me/{bot_username}?start={tag}"
        desc = data.get("desc", "")
        downloads = data.get("downloads", 0)
        text += f"🔗 {link}\n"
        if desc:
            text += f"📝 Описание: {desc}\n"
        text += f"📥 Скачиваний: {downloads}\n\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

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
    bot.send_message(message.chat.id, f"📦 Начинаю выгрузку всех файлов ({len(files_only)} шт.)...\n*Напиши `/stop` для отмены*", parse_mode="Markdown")
    
    for tag, data in files_only.items():
        if not active_processes.get(ADMIN_ID, True):
            bot.send_message(message.chat.id, "🛑 Выгрузка прервана.")
            return
        try:
            bot.copy_message(message.chat.id, STORAGE_CHANNEL_ID, data.get("msg_id"))
            time.sleep(0.3)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка выгрузки тега `{tag}`: {e}", parse_mode="Markdown")
            
    if active_processes.get(ADMIN_ID, True):
        bot.send_message(message.chat.id, "✅ **Выгрузка всех файлов завершена!**", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data.startswith("files_page_"):
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
                save_mapping_data(mapping)
                send_file_to_user(chat_id, file_key)
            else:
                bot.send_message(chat_id, "❌ Файл не найден.")

    elif call.data == "open_profile":
        first_name = user.first_name
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        
        mapping = load_mapping()
        total_downloads = sum(item.get("downloads", 0) for key, item in mapping.items() if key != "_settings")

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
            try:
                bot.edit_message_caption(
                    caption=profile_caption,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard(),
                    parse_mode="Markdown"
                )
            except Exception:
                bot.edit_message_text(
                    text=profile_caption,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard(),
                    parse_mode="Markdown"
                )
        bot.answer_callback_query(call.id)

    elif call.data == "back_to_main":
        caption_text = (
            "👋 Привет!\n\n"
            "💬 Я файловый менеджер и храню файлы с канала @goat1488_67!\n\n"
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
            try:
                bot.edit_message_caption(
                    caption=caption_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard()
                )
            except Exception:
                bot.edit_message_text(
                    text=caption_text,
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
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
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
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
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

                bot.send_message(message.chat.id, f"✏️ Файл с тегом `{tag}` успешно обновлен!", parse_mode="Markdown")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ошибка при обновлении: {e}")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка: тег не найден в базе.")

    admin_states.pop(ADMIN_ID, None)

@bot.message_handler(commands=["del"])
def delete_file(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Недостаточно прав для выполнения этой команды.")
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
        text = "🔗 **Текущие каналы для проверки подписки:**\n\n"
        for ch in channels:
            text += f"• `{ch}`\n"
        text += (
            "\n⚙️ **Управление:**\n"
            "• Добавить: `/links add @channel`\n"
            "• Удалить: `/links del @channel`"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        return

    action = args[1].lower()
    if len(args) < 3:
        bot.send_message(message.chat.id, "⚠️ Укажи юзернейм канала, например: `/links add @goat1488_67`", parse_mode="Markdown")
        return

    channel_target = args[2].strip()
    if not channel_target.startswith("@"):
        channel_target = "@" + channel_target

    if action == "add":
        if channel_target not in channels:
            channels.append(channel_target)
            settings["channels"] = channels
            save_mapping_data(mapping)
            bot.send_message(message.chat.id, f"✅ Канал `{channel_target}` успешно добавлен в проверку подписки!")
        else:
            bot.send_message(message.chat.id, f"⚠️ Канал `{channel_target}` уже есть в списке.")
    elif action == "del":
        if channel_target in channels:
            if len(channels) <= 1:
                bot.send_message(message.chat.id, "❌ Нельзя удалить последний канал! Должен оставаться хотя бы один.")
                return
            channels.remove(channel_target)
            settings["channels"] = channels
            save_mapping_data(mapping)
            bot.send_message(message.chat.id, f"🗑 Канал `{channel_target}` удален из проверки подписки.")
        else:
            bot.send_message(message.chat.id, f"❌ Канал `{channel_target}` не найден в списке.")

@bot.message_handler(func=lambda message: True, content_types=["text", "photo", "video", "document", "audio", "sticker", "animation"])
def forward_user_messages(message):
    if message.text and message.text.startswith("/"):
        return

    user = message.from_user
    user_id = user.id
    name = user.first_name
    
    user_footer = f"От: [{name}](tg://user?id={user_id})"

    try:
        if message.caption:
            new_caption = f"{message.caption}\n\n{user_footer}"
            if message.photo:
                bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=new_caption, parse_mode="Markdown")
            elif message.document:
                bot.send_document(ADMIN_ID, message.document.file_id, caption=new_caption, parse_mode="Markdown")
            elif message.video:
                bot.send_video(ADMIN_ID, message.video.file_id, caption=new_caption, parse_mode="Markdown")
        elif message.text:
            full_text = f"{message.text}\n\n{user_footer}"
            bot.send_message(ADMIN_ID, full_text, parse_mode="Markdown")
        else:
            bot.copy_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(ADMIN_ID, user_footer, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка пересылки сообщения админу: {e}")

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
