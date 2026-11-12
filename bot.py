import json
import os
import random
import time
import io
import hashlib
import base64
import zipfile
import qrcode
from datetime import datetime, time as dtime
from threading import Thread
import requests
import telebot
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from flask import Flask

# ==========================================
# ⚙️ ОСНОВНЫЕ НАСТРОЙКИ И ПЕРЕМЕННЫЕ
# ==========================================
TOKEN = "8847975926:AAFjFoyp14iwMr8YhqLigX6Xww1RBueYh3I"
ADMIN_ID = 6795794125
STORAGE_CHANNEL_ID = -1003931200359
FEEDBACK_BOT_URL = "https://t.me/feedbackls_bot"
VT_API_KEY = "fa5af0a32f4aa92be1536149bcf01321aaab83104c67ff7e50c37ff5fa64dcc8"

# Ссылка на сайт (кнопки на файлах убраны по вашему запросу)
SITE_URL = "https://popka22867.github.io/Adapter/"

START_TIME = datetime(2026, 10, 25, 16, 33, 52).timestamp()
# ==========================================

bot = telebot.TeleBot(TOKEN)

admin_states = {}
active_processes = {}

ACHIEVEMENTS_CONFIG = [
    ("dl_1", "dl", 1),
    ("dl_5", "dl", 5),
    ("dl_10", "dl", 10),
    ("dl_20", "dl", 20),
    ("dl_50", "dl", 50),
    ("dl_67", "dl", 67),
    ("dl_100", "dl", 100),
    ("dl_200", "dl", 200),
    ("dl_228", "dl", 228),
    ("dl_500", "dl", 500),
    ("dl_1000", "dl", 1000),
    ("dl_1337", "dl", 1337),
    ("dl_1488", "dl", 1488),
    ("ref_1", "ref", 1),
    ("ref_5", "ref", 5),
    ("ref_10", "ref", 10),
    ("ref_20", "ref", 20),
    ("ref_50", "ref", 50),
    ("ref_67", "ref", 67),
    ("ref_100", "ref", 100),
    ("rate_1", "rate", 1),
    ("rate_10", "rate", 10),
    ("rate_25", "rate", 25),
    ("sug_1", "sug", 1),
    ("sug_5", "sug", 5),
    ("sug_15", "sug", 15),
    ("admin_god", "admin", 1),
]

LANGS = {
    "uk": {
        "lang_name": "🇺🇦 Українська",
        "welcome": "👋 Привіт, {name}{title_part}!\n\n💬 Я файловий менеджер і зберігаю файли з каналу @goat1488_67!\n\n🔽 Використовуй кнопки нижче для навігації",
        "btn_channel": "📢 Наш канал",
        "btn_profile": "⚙️ Профіль",
        "btn_feedback": "👤 Зворотний зв'язок",
        "btn_suggest": "📤 Запропонувати файл",
        "btn_commands": "📋 Команди",
        "btn_lang": "🌐 Мова: Українська",
        "select_lang": "Оберіть мову / Choose language:",
        "lang_set": "✅ Мову успішно змінено!",
        "profile_title": "👤 Профіль",
        "profile_id": "🆔 ID",
        "profile_name": "👤 Ім'я",
        "profile_title_line": "🎖 Титул",
        "no_title": "Не вибрано",
        "profile_username": "👤 Username",
        "profile_uptime": "⏳ Час роботи бота",
        "profile_my_dl": "📥 Твоїх завантажень",
        "profile_total_dl": "📥 Всього завантажень у боті",
        "profile_fav_count": "⭐ Файлів в обраному",
        "btn_favorites": "⭐ Обране",
        "btn_fav_add": "⭐ Додати в обране",
        "btn_fav_del": "🗑 Видалити з обраного",
        "fav_added": "✅ Файл додано до обраного!",
        "fav_removed": "🗑 Файл видалено з обраного!",
        "favorites_title": "⭐ **Твоє обране:**",
        "favorites_empty": "📭 Твоє обране поки що порожнє.",
        "back": "🔙 Назад",
        "rate_thanks": "⭐ Дякуємо за оцінку: ",
        "rate_prompt": "Оцініть файл або надішліть скаргу:",
        "report_btn": "🚨 Поскаржитися на файл",
        "report_title": "🚨 **СКАРГА НА ФАЙЛ**",
        "report_tag": "🔗 Тег",
        "report_reason": "📋 Причина",
        "report_user": "👤 Від користувача",
        "report_success": "✅ Скарга успішно відправлена адміністрації!",
        "reason_virus": "🦠 Містяться віруси / ПЗ",
        "reason_outdated": "🔄 Застаріла версія (є оновлення)",
        "reason_broken": "🚫 Битий / неробочий файл",
        "reason_other": "❌ Інша причина",
        "file_not_found": "❌ Файл не знайдено.",
        "sub_required": "❌ Для отримання файлу необхідно підписатися на наш канал:",
        "sub_btn": "📢 Підписатися на ",
        "sub_check_btn": "🔄 Я підписався (-лась)",
        "sub_fail": "❌ Ви підписалися ще не на всі канали!",
        "sub_success": "✅ Підписку підтверджено!",
        "help_admin_title": "📋 Доступні команди (Адміністратор):",
        "help_user_title": "📋 Доступні команди:",
        "cmd_start": "Запустити бота",
        "cmd_suggest": "Запропонувати файл",
        "cmd_check_vt": "Перевірити через VT",
        "cmd_help": "Список команд",
        "cmd_add": "Додати файл в базу",
        "cmd_edit": "Змінити файл за тегом",
        "cmd_files": "Список файлів бази",
        "cmd_search": "Пошук файлу",
        "cmd_del": "Видалити файл за тегом",
        "cmd_links": "Канали підписки",
        "cmd_full": "Вивантажити всі файли",
        "cmd_stop": "Зупинити вивантаження",
        "cmd_db": "Завантажити головну базу",
        "cmd_update_db": "Оновити базу описів",
        "cmd_stats_files": "Статистика та оцінки файлів",
        "admin_no_rights": "❌ Недостатньо прав для виконання цієї команди.",
        "admin_add_prompt": "📤 Надішліть файл, фото або відео з тегом та описом в підписі (або ZIP-архів для масового імпорту):",
        "admin_edit_usage": "⚠️ Вкажіть тег: `/edit tag`",
        "admin_edit_not_found": "❌ Тег не знайдено в базі.",
        "admin_edit_prompt": "✏️ Надішліть новий файл для тега",
        "admin_db_not_found": "❌ Файл db.txt не знайдено в каналі.",
        "admin_search_usage": "⚠️ Укажіть текст для пошуку: `/search запит`",
        "admin_search_empty": "❌ Нічого не знайдено за вашим запитом.",
        "admin_files_empty": "📭 Список файлів порожній.",
        "admin_full_empty": "📭 База даних порожня, файлів немає.",
        "admin_full_start": "📦 Починаю вигрузку всіх файлів... Напишіть /stop для скасування",
        "admin_full_stop": "🛑 Вигрузку скасовано.",
        "admin_full_done": "✅ Вигрузку всіх файлів завершено!",
        "admin_saved": "✅ Збережено тег:",
        "admin_updated": "✏️ Файл успішно оновлено!",
        "vt_prompt": "🛡 Надішліть файл або посилання для перевірки через VirusTotal:",
        "vt_checking_url": "🛡 Перевіряємо посилання через VirusTotal...",
        "vt_checking_file": "🛡 Перевіряємо файл через VirusTotal...",
        "vt_success_url": "✅ Посилання перевірено!\n\n🔗 Звіт:",
        "vt_success_file": "✅ Файл успішно відправлено на перевірку!\n\n🔗 Звіт:",
        "vt_already": "ℹ️ Файл вже є в базі VirusTotal!\n\n🔗 Звіт:",
        "suggest_prompt": "📤 Надішліть файл, фото або відео з тегом і описом в підписі (наприклад: `my_tag Опис файлу`):",
        "suggest_success": "✅ Файл успішно відправлено адміністратору на розгляд!",
        "links_header": "🔗 **Канали обов'язкової підписки:**\n\n",
        "links_usage": "⚠️ Використання:\n`/links add @channel` — додати канал\n`/links del @channel` — видалити канал",
        "links_added": "✅ Успішно додано канал підписки:",
        "links_deleted": "🗑 Успішно видалено канал підписки:",
        "db_empty": "📭 База порожня.",
        "stats_title": "📊 **Модерація оцінок та рейтингу файлів:**",
        "stats_row": "🔹 `#{tag}` | Завантажень: {downloads} | Оцінок: {ratings} | Середній бал: ⭐ {avg}/5",
        "error_generic": "❌ Помилка: {error}",
        "db_updated": "✅ Базу даних успішно оновлено! Перевірено та підтягнуто описів: {count}",
        "btn_prev": "⬅️ Назад",
        "btn_next": "Далі ➡️",
        "files_list_title": "📂 Список файлів (Сторінка {page} з {total}):",
        "search_results_title": "🔍 Результати пошуку за запитом '{query}':",
        "file_desc_line": "📝 Опис: {desc}",
        "file_downloads_line": "📥 Завантажень: {count}",
        "page_suffix": "(Сторінка {page}/{total})",
        "full_tag_error": "⚠️ Помилка вивантаження тега {tag}: {error}",
        "uptime_fmt": "{d}д {h}г {m}хв {s}с",
        "status_approved": "✅ СХВАЛЕНО",
        "status_approved_edited": "✅ СХВАЛЕНО ТА ВІДРЕДАГОВАНО",
        "status_rejected": "❌ ВІДХИЛЕНО",
        "status_rejected_reason": "❌ ВІДХИЛЕНО: {reason}",
        "toast_approved": "Успішно схвалено!",
        "toast_rejected": "Відхилено.",
        "suggest_approved_user": "✅ Ваш запропонований файл схвалено!",
        "suggest_rejected_user": "❌ Ваш запропонований файл відхилено.",
        "suggest_approved_link_user": "✅ Вашу пропозицію схвалено: {link}",
        "suggest_rejected_reason_user": "❌ Вашу пропозицію відхилено.\nПричина: {reason}",
        "edit_approve_prompt": "✏️ Введіть новий тег та опис через пробіл (наприклад: `new_tag Опис`):",
        "reject_reason_prompt": "💬 Введіть причину відхилення:",
        "notify_new_available": "🚀 Доступний новий файл!\n🔗 {link}\n📝 {desc}",
        "notify_new_added": "🚀 Додано новий файл!\n🔗 {link}\n📝 {desc}",
        "notify_updated": "🔄 Доступне оновлення файлу!\n🔗 {link}\n📝 {desc}",
        "file_deleted": "🗑 Видалено: {tag}",
        "link_exists": "⚠️ Канал {channel} вже є в списку.",
        "link_cannot_delete": "⚠️ Не можна видалити останній канал або канал не знайдено.",
        "suggest_need_tag": "⚠️ Вкажіть тег!",
        "btn_approve": "✅ Схвалити",
        "btn_reject": "❌ Відхилити",
        "btn_edit_approve": "✏️ Змінити та схвалити",
        "btn_edit_reject": "✏️ Змінити та відхилити",
        "suggested_by": "Запропонував(-ла):",
        "vt_no_key": "⚠️ Ключ VT API не налаштовано.",
        "vt_error": "❌ Помилка VirusTotal: {error}",
        "vt_send_file_or_link": "⚠️ Надішліть файл або посилання.",
        "arg_tag": "тег",
        "arg_query": "запит",
        "daily_stats_title": "📊 **Щоденна статистика бота**",
        "daily_stats_date": "📅 Дата: {date}",
        "daily_stats_files": "📂 Всього файлів: {count}",
        "daily_stats_downloads": "📥 Всього завантажень: {count}",
        "btn_files": "📂 Файли",
        "files_menu_title": "📂 Оберіть розділ:",
        "btn_new": "🆕 Новинки",
        "btn_top": "🔥 Популярні",
        "btn_rated": "⭐ Найкращі за оцінкою",
        "btn_search": "🔍 Пошук",
        "list_title": "{name} · {page}/{total}",
        "pick_file": "👇 Оберіть файл:",
        "search_prompt": "🔍 Введіть пошуковий запит:",
        "rating_line": "⭐ Рейтинг: {avg}/5 ({n}) · 📥 {dl}",
        "btn_notify_on": "🔔 Сповіщення: увімк.",
        "btn_notify_off": "🔕 Сповіщення: вимк.",
        "notify_on_toast": "🔔 Сповіщення увімкнено",
        "notify_off_toast": "🔕 Сповіщення вимкнено",
        "flood_warn": "⏳ Не так швидко! Зачекайте кілька секунд.",
        "banned_msg": "🚫 Вам обмежено доступ до бота.",
        "ban_usage": "⚠️ Використання: /ban ID або /unban ID",
        "ban_done": "🚫 Користувача {uid} заблоковано.",
        "unban_done": "✅ Користувача {uid} розблоковано.",
        "ban_admin": "⚠️ Не можна заблокувати адміністратора.",
        "cmd_ban": "Заблокувати користувача",
        "cmd_unban": "Розблокувати користувача",
        "cmd_broadcast": "Розсилка всім користувачам",
        "cmd_stats": "Загальна статистика бота",
        "arg_id": "ID",
        "arg_text": "текст",
        "broadcast_usage": "⚠️ Використання: /broadcast текст",
        "broadcast_started": "📣 Розсилку розпочато...",
        "broadcast_done": "📣 Розсилку завершено. Надіслано: {ok}, помилок: {fail}",
        "stats_overview": "📊 Статистика бота\n\n👥 Користувачів: {users}\n🚫 Заблоковано: {banned}\n📂 Файлів: {files}\n📥 Завантажень: {downloads}\n\n🔥 Топ-5:\n{top}",
        "btn_qr_code": "📷 QR-код",
        "qr_code_caption": "📷 QR-код для файлу `{tag}`:\n🔗 Посилання: {link}",
        "btn_achievements": "🏆 Досягнення та Титули",
        "btn_select_title": "🎖 Обрати титул",
        "btn_clear_title": "❌ Зняти титул",
        "title_equipped": "✅ Встановлено титул: {title}",
        "title_cleared": "🗑 Титул знято!",
        "select_title_prompt": "🎖 Оберіть титул із відкритих досягнень (він буде відображатися у /start):",
        "no_titles_unlocked": "🔒 У тебе поки немає відкритих титулів. Качай файли, клич друзів або пропонуй файли!",
        "ref_menu_title": "🏆 <b>Досягнення та Реферали</b>\n\n🔗 Твоє реферальне посилання:\n<code>{ref_link}</code>\n\n👥 Друзів: <b>{ref_count}</b> | 📥 Завантажень: <b>{dl_count}</b>\n⭐ Оцінок: <b>{rate_count}</b> | 📤 Прийнято файлів: <b>{sug_count}</b>\n🎖 Активний титул: <b>{cur_title}</b>\n\n📜 <b>Список титулів:</b>\n{achievements}",
        "zip_upload_start": "📦 Розпаковую ZIP-архів та масово додаю файли в базу...",
        "zip_upload_done": "✅ Успішно імпортовано файлів з архіву: {count}",
        "zip_error": "❌ Помилка обробки ZIP-архіву: {error}",
        "title_dl_1": "Новачок",
        "title_dl_5": "Свій в темі",
        "title_dl_10": "Шукач",
        "title_dl_20": "Файловий краш",
        "title_dl_50": "Кібер-мисливець",
        "title_dl_67": "Six Seven",
        "title_dl_100": "Перший чемпіон",
        "title_dl_200": "Кібер-машина",
        "title_dl_228": "Андерграунд легенда",
        "title_dl_500": "Володар трафіку",
        "title_dl_1000": "Архітектор бази",
        "title_dl_1337": "Elite Hax0r",
        "title_dl_1488": "Абсолютний Батько",
        "title_ref_1": "Провідник",
        "title_ref_5": "Душа компанії",
        "title_ref_10": "Лідер скваду",
        "title_ref_20": "Амбасадор",
        "title_ref_50": "Інфлюенсер",
        "title_ref_67": "Six Seven Squad",
        "title_ref_100": "Магнат ком'юніті",
        "title_rate_1": "Перший погляд",
        "title_rate_10": "Тру Критик",
        "title_rate_25": "Головний Ревізор",
        "title_sug_1": "Помічник",
        "title_sug_5": "Постачальник годноти",
        "title_sug_15": "Меценат каналу",
        "title_admin_god": "👑 Головний Адмін",
        "desc_dl_1": "1 завантаження",
        "desc_dl_5": "5 завантажень",
        "desc_dl_10": "10 завантажень",
        "desc_dl_20": "20 завантажень",
        "desc_dl_50": "50 завантажень",
        "desc_dl_67": "67 завантажень",
        "desc_dl_100": "100 завантажень",
        "desc_dl_200": "200 завантажень",
        "desc_dl_228": "228 завантажень",
        "desc_dl_500": "500 завантажень",
        "desc_dl_1000": "1000 завантажень",
        "desc_dl_1337": "1337 завантажень",
        "desc_dl_1488": "1488 завантажень",
        "desc_ref_1": "1 друг",
        "desc_ref_5": "5 друзів",
        "desc_ref_10": "10 друзів",
        "desc_ref_20": "20 друзів",
        "desc_ref_50": "50 друзів",
        "desc_ref_67": "67 друзів",
        "desc_ref_100": "100 друзів",
        "desc_rate_1": "1 оцінка",
        "desc_rate_10": "10 оцінок",
        "desc_rate_25": "25 оцінок",
        "desc_sug_1": "1 схвалений файл",
        "desc_sug_5": "5 схвалених файлів",
        "desc_sug_15": "15 схвалених файлів",
        "desc_admin_god": "Спеціальний статус адміністратора"
    },
    "ru": {
        "lang_name": "🇷🇺 Русский",
        "welcome": "👋 Привет, {name}{title_part}!\n\n💬 Я файловый менеджер и храню файлы с канала @goat1488_67!\n\n🔽 Используй кнопки ниже для навигации",
        "btn_channel": "📢 Наш канал",
        "btn_profile": "⚙️ Профиль",
        "btn_feedback": "👤 Обратная связь",
        "btn_suggest": "📤 Предложить файл",
        "btn_commands": "📋 Команды",
        "btn_lang": "🌐 Язык: Русский",
        "select_lang": "Выберите язык / Choose language:",
        "lang_set": "✅ Язык успешно изменен!",
        "profile_title": "👤 Профиль",
        "profile_id": "🆔 ID",
        "profile_name": "👤 Имя",
        "profile_title_line": "🎖 Титул",
        "no_title": "Не выбран",
        "profile_username": "👤 Username",
        "profile_uptime": "⏳ Время работы бота",
        "profile_my_dl": "📥 Твоих скачиваний",
        "profile_total_dl": "📥 Всего скачиваний в боте",
        "profile_fav_count": "⭐ Файлов в избранном",
        "btn_favorites": "⭐ Избранное",
        "btn_fav_add": "⭐ В избранное",
        "btn_fav_del": "🗑 Убрать из избранного",
        "fav_added": "✅ Файл добавлен в избранное!",
        "fav_removed": "🗑 Файл удален из избранного!",
        "favorites_title": "⭐ **Твое избранное:**",
        "favorites_empty": "📭 Твое избранное пока пусто.",
        "back": "🔙 Назад",
        "rate_thanks": "⭐ Спасибо за оценку: ",
        "rate_prompt": "Оцените файл или отправьте жалобу:",
        "report_btn": "🚨 Пожаловаться на файл",
        "report_title": "🚨 **ЖАЛОБА НА ФАЙЛ**",
        "report_tag": "🔗 Тег",
        "report_reason": "📋 Причина",
        "report_user": "👤 От пользователя",
        "report_success": "✅ Жалоба успешно отправлена администрации!",
        "reason_virus": "🦠 Содержатся вирусы / ПО",
        "reason_outdated": "🔄 Устаревшая версия (вышло обновление)",
        "reason_broken": "🚫 Битый / нерабочий файл",
        "reason_other": "❌ Другая причина",
        "file_not_found": "❌ Файл не найден.",
        "sub_required": "❌ Для получения файла необходимо подписаться на наш канал:",
        "sub_btn": "📢 Подписаться на ",
        "sub_check_btn": "🔄 Я подписался (-ась)",
        "sub_fail": "❌ Вы подписались еще не на все каналы!",
        "sub_success": "✅ Подписка подтверждена!",
        "help_admin_title": "📋 Доступные команды (Администратор):",
        "help_user_title": "📋 Доступные команды:",
        "cmd_start": "Запустить бота",
        "cmd_suggest": "Предложить файл",
        "cmd_check_vt": "Проверить через VT",
        "cmd_help": "Список команд",
        "cmd_add": "Добавить файл в базу",
        "cmd_edit": "Изменить файл по тегу",
        "cmd_files": "Список файлов базы",
        "cmd_search": "Поиск файла",
        "cmd_del": "Удалить файл по тегу",
        "cmd_links": "Каналы подписки",
        "cmd_full": "Выгрузить все файлы",
        "cmd_stop": "Остановить выгрузку",
        "cmd_db": "Скачать главную базу",
        "cmd_update_db": "Обновить базу описаний",
        "cmd_stats_files": "Статистика и оценки файлов",
        "admin_no_rights": "❌ Недостаточно прав для выполнения этой команды.",
        "admin_add_prompt": "📤 Отправьте файл, фото или видео с тегом и описанием (либо ZIP-архив для массового импорта):",
        "admin_edit_usage": "⚠️ Укажите тег: `/edit tag`",
        "admin_edit_not_found": "❌ Тег не найден в базе.",
        "admin_edit_prompt": "✏️ Отправьте новый файл для тега",
        "admin_db_not_found": "❌ Файл db.txt не найден в канале.",
        "admin_search_usage": "⚠️ Укажите тег для поиска: `/search запрос`",
        "admin_search_empty": "❌ Ничего не найдено по вашему запросу.",
        "admin_files_empty": "📭 Список файлов пуст.",
        "admin_full_empty": "📭 База данных пуста, файлов нет.",
        "admin_full_start": "📦 Начинаю выгрузку всех файлов... Напишите /stop для отмены",
        "admin_full_stop": "🛑 Выгрузка прервана.",
        "admin_full_done": "✅ Выгрузка всех файлов завершена!",
        "admin_saved": "✅ Сохранен тег:",
        "admin_updated": "✏️ Файл успешно обновлен!",
        "vt_prompt": "🛡 Отправьте файл или текстовую ссылку для проверки через VirusTotal:",
        "vt_checking_url": "🛡 Проверяем ссылку через VirusTotal...",
        "vt_checking_file": "🛡 Проверяем файл через VirusTotal...",
        "vt_success_url": "✅ Ссылка проверена!\n\n🔗 Отчет:",
        "vt_success_file": "✅ Файл успешно отправлен на проверку!\n\n🔗 Отчет:",
        "vt_already": "ℹ️ Файл уже есть в базе VirusTotal!\n\n🔗 Отчет:",
        "suggest_prompt": "📤 Отправьте файл, фото или видео с тегом и описанием в подписи (например: `my_tag Описание файла`):",
        "suggest_success": "✅ Файл успешно отправлен администрации на рассмотрение!",
        "links_header": "🔗 **Каналы обязательной подписки:**\n\n",
        "links_usage": "⚠️ Использование:\n`/links add @channel` — добавить канал\n`/links del @channel` — удалить канал",
        "links_added": "✅ Успешно добавлен канал подписки:",
        "links_deleted": "🗑 Успешно удален канал подписки:",
        "db_empty": "📭 База пуста.",
        "stats_title": "📊 **Модерация оценок и рейтинга файлов:**",
        "stats_row": "🔹 `#{tag}` | Скачиваний: {downloads} | Оценок: {ratings} | Средний балл: ⭐ {avg}/5",
        "error_generic": "❌ Ошибка: {error}",
        "db_updated": "✅ База данных успешно обновлена! Проверено и подтянуто описаний: {count}",
        "btn_prev": "⬅️ Назад",
        "btn_next": "Вперёд ➡️",
        "files_list_title": "📂 Список файлов (Страница {page} из {total}):",
        "search_results_title": "🔍 Результаты поиска по запросу '{query}':",
        "file_desc_line": "📝 Описание: {desc}",
        "file_downloads_line": "📥 Скачиваний: {count}",
        "page_suffix": "(Страница {page}/{total})",
        "full_tag_error": "⚠️ Ошибка выгрузки тега {tag}: {error}",
        "uptime_fmt": "{d}д {h}ч {m}мин {s}с",
        "status_approved": "✅ ОДОБРЕНО",
        "status_approved_edited": "✅ ОДОБРЕНО И ОТРЕДАКТИРОВАНО",
        "status_rejected": "❌ ОТКЛОНЕНО",
        "status_rejected_reason": "❌ ОТКЛОНЕНО: {reason}",
        "toast_approved": "Успешно одобрено!",
        "toast_rejected": "Отклонено.",
        "suggest_approved_user": "✅ Ваш предложенный файл одобрен!",
        "suggest_rejected_user": "❌ Ваш предложенный файл отклонён.",
        "suggest_approved_link_user": "✅ Ваше предложение одобрено: {link}",
        "suggest_rejected_reason_user": "❌ Ваше предложение отклонено.\nПричина: {reason}",
        "edit_approve_prompt": "✏️ Введите новый тег и описание через пробел (например: `new_tag Описание`):",
        "reject_reason_prompt": "💬 Введите причину отклонения:",
        "notify_new_available": "🚀 Доступен новый файл!\n🔗 {link}\n📝 {desc}",
        "notify_new_added": "🚀 Добавлен новый файл!\n🔗 {link}\n📝 {desc}",
        "notify_updated": "🔄 Доступно обновление файла!\n🔗 {link}\n📝 {desc}",
        "file_deleted": "🗑 Удалено: {tag}",
        "link_exists": "⚠️ Канал {channel} уже есть в списке.",
        "link_cannot_delete": "⚠️ Нельзя удалить последний канал или канал не найден.",
        "suggest_need_tag": "⚠️ Укажите тег!",
        "btn_approve": "✅ Одобрить",
        "btn_reject": "❌ Отклонить",
        "btn_edit_approve": "✏️ Изменить и одобрить",
        "btn_edit_reject": "✏️ Изменить и отклонить",
        "suggested_by": "Предложил(-а):",
        "vt_no_key": "⚠️ Ключ VT API не настроен.",
        "vt_error": "❌ Ошибка VirusTotal: {error}",
        "vt_send_file_or_link": "⚠️ Отправьте файл или ссылку.",
        "arg_tag": "тег",
        "arg_query": "запрос",
        "daily_stats_title": "📊 **Ежедневная статистика бота**",
        "daily_stats_date": "📅 Дата: {date}",
        "daily_stats_files": "📂 Всего файлов: {count}",
        "daily_stats_downloads": "📥 Всего скачиваний: {count}",
        "btn_files": "📂 Файлы",
        "files_menu_title": "📂 Выберите раздел:",
        "btn_new": "🆕 Новинки",
        "btn_top": "🔥 Популярные",
        "btn_rated": "⭐ Лучшие по оценке",
        "btn_search": "🔍 Поиск",
        "list_title": "{name} · {page}/{total}",
        "pick_file": "👇 Выберите файл:",
        "search_prompt": "🔍 Введите поисковый запрос:",
        "rating_line": "⭐ Рейтинг: {avg}/5 ({n}) · 📥 {dl}",
        "btn_notify_on": "🔔 Уведомления: вкл.",
        "btn_notify_off": "🔕 Уведомления: выкл.",
        "notify_on_toast": "🔔 Уведомления включены",
        "notify_off_toast": "🔕 Уведомления отключены",
        "flood_warn": "⏳ Не так быстро! Подождите несколько секунд.",
        "banned_msg": "🚫 Вам ограничен доступ к боту.",
        "ban_usage": "⚠️ Использование: /ban ID или /unban ID",
        "ban_done": "🚫 Пользователь {uid} заблокирован.",
        "unban_done": "✅ Пользователь {uid} разблокирован.",
        "ban_admin": "⚠️ Нельзя заблокировать администратора.",
        "cmd_ban": "Заблокировать пользователя",
        "cmd_unban": "Разблокировать пользователя",
        "cmd_broadcast": "Рассылка всем пользователям",
        "cmd_stats": "Общая статистика бота",
        "arg_id": "ID",
        "arg_text": "текст",
        "broadcast_usage": "⚠️ Использование: /broadcast текст",
        "broadcast_started": "📣 Рассылка начата...",
        "broadcast_done": "📣 Рассылка завершена. Отправлено: {ok}, ошибок: {fail}",
        "stats_overview": "📊 Статистика бота\n\n👥 Пользователей: {users}\n🚫 Заблокировано: {banned}\n📂 Файлов: {files}\n📥 Скачиваний: {downloads}\n\n🔥 Топ-5:\n{top}",
        "btn_qr_code": "📷 QR-код",
        "qr_code_caption": "📷 QR-код для файла `{tag}`:\n🔗 Ссылка: {link}",
        "btn_achievements": "🏆 Достижения и Титулы",
        "btn_select_title": "🎖 Выбрать титул",
        "btn_clear_title": "❌ Снять титул",
        "title_equipped": "✅ Установлен титул: {title}",
        "title_cleared": "🗑 Титул снят!",
        "select_title_prompt": "🎖 Выберите титул из открытых достижений (он будет отображаться в /start):",
        "no_titles_unlocked": "🔒 У тебя пока нет открытых титулов. Качай файлы, зови друзей или предлагай файлы!",
        "ref_menu_title": "🏆 <b>Достижения и Рефералы</b>\n\n🔗 Твоя реферальная ссылка:\n<code>{ref_link}</code>\n\n👥 Друзей: <b>{ref_count}</b> | 📥 Скачиваний: <b>{dl_count}</b>\n⭐ Оценок: <b>{rate_count}</b> | 📤 Принято файлов: <b>{sug_count}</b>\n🎖 Активный титул: <b>{cur_title}</b>\n\n📜 <b>Список титулов:</b>\n{achievements}",
        "zip_upload_start": "📦 Распаковываю ZIP-архив и массово добавляю файлы в базу...",
        "zip_upload_done": "✅ Успешно импортировано файлов из архива: {count}",
        "zip_error": "❌ Ошибка обработки ZIP-архива: {error}",
        "title_dl_1": "Новичок",
        "title_dl_5": "Свой в теме",
        "title_dl_10": "Искатель",
        "title_dl_20": "Файловый краш",
        "title_dl_50": "Кибер-охотник",
        "title_dl_67": "Six Seven",
        "title_dl_100": "Первый чемпион",
        "title_dl_200": "Кибер-машина",
        "title_dl_228": "Андерграунд легенда",
        "title_dl_500": "Повелитель трафика",
        "title_dl_1000": "Архитектор базы",
        "title_dl_1337": "Elite Hax0r",
        "title_dl_1488": "Абсолютный Батя",
        "title_ref_1": "Проводник",
        "title_ref_5": "Душа компании",
        "title_ref_10": "Лидер сквада",
        "title_ref_20": "Амбассадор",
        "title_ref_50": "Инфлюенсер",
        "title_ref_67": "Six Seven Squad",
        "title_ref_100": "Магнат комьюнити",
        "title_rate_1": "Первый взгляд",
        "title_rate_10": "Тру Критик",
        "title_rate_25": "Главный Ревизор",
        "title_sug_1": "Помощник",
        "title_sug_5": "Поставщик годноты",
        "title_sug_15": "Меценат канала",
        "title_admin_god": "👑 Главный Адмін",
        "desc_dl_1": "1 скачивание",
        "desc_dl_5": "5 скачиваний",
        "desc_dl_10": "10 скачиваний",
        "desc_dl_20": "20 скачиваний",
        "desc_dl_50": "50 скачиваний",
        "desc_dl_67": "67 скачиваний",
        "desc_dl_100": "100 скачиваний",
        "desc_dl_200": "200 скачиваний",
        "desc_dl_228": "228 скачиваний",
        "desc_dl_500": "500 скачиваний",
        "desc_dl_1000": "1000 скачиваний",
        "desc_dl_1337": "1337 скачиваний",
        "desc_dl_1488": "1488 скачиваний",
        "desc_ref_1": "1 друг",
        "desc_ref_5": "5 друзей",
        "desc_ref_10": "10 друзей",
        "desc_ref_20": "20 друзей",
        "desc_ref_50": "50 друзей",
        "desc_ref_67": "67 друзей",
        "desc_ref_100": "100 друзей",
        "desc_rate_1": "1 оценка",
        "desc_rate_10": "10 оценок",
        "desc_rate_25": "25 оценок",
        "desc_sug_1": "1 одобренный файл",
        "desc_sug_5": "5 одобренных файлов",
        "desc_sug_15": "15 одобренных файлов",
        "desc_admin_god": "Специальный статус администратора"
    },
    "en": {
        "lang_name": "🇬🇧 English",
        "welcome": "👋 Hello, {name}{title_part}!\n\n💬 I am a file manager storing files from @goat1488_67!\n\n🔽 Use the buttons below to navigate",
        "btn_channel": "📢 Our channel",
        "btn_profile": "⚙️ Profile",
        "btn_feedback": "👤 Feedback",
        "btn_suggest": "📤 Suggest file",
        "btn_commands": "📋 Commands",
        "btn_lang": "🌐 Language: English",
        "select_lang": "Choose language:",
        "lang_set": "✅ Language successfully changed!",
        "profile_title": "👤 Profile",
        "profile_id": "🆔 ID",
        "profile_name": "👤 Name",
        "profile_title_line": "🎖 Title",
        "no_title": "None",
        "profile_username": "👤 Username",
        "profile_uptime": "⏳ Bot Uptime",
        "profile_my_dl": "📥 Your downloads",
        "profile_total_dl": "📥 Total downloads in bot",
        "profile_fav_count": "⭐ Files in favorites",
        "btn_favorites": "⭐ Favorites",
        "btn_fav_add": "⭐ Add to favorites",
        "btn_fav_del": "🗑 Remove from favorites",
        "fav_added": "✅ File added to favorites!",
        "fav_removed": "🗑 File removed from favorites!",
        "favorites_title": "⭐ **Your favorites:**",
        "favorites_empty": "📭 Your favorites list is empty.",
        "back": "🔙 Back",
        "rate_thanks": "⭐ Thanks for rating: ",
        "rate_prompt": "Rate the file or send a report:",
        "report_btn": "🚨 Report file",
        "report_title": "🚨 **FILE REPORT**",
        "report_tag": "🔗 Tag",
        "report_reason": "📋 Reason",
        "report_user": "👤 From user",
        "report_success": "✅ Report successfully sent to administration!",
        "reason_virus": "🦠 Contains viruses / malware",
        "reason_outdated": "🔄 Outdated version (update available)",
        "reason_broken": "🚫 Broken / non-working file",
        "reason_other": "❌ Other reason",
        "file_not_found": "❌ File not found.",
        "sub_required": "❌ To receive the file, you must subscribe to our channel:",
        "sub_btn": "📢 Subscribe to ",
        "sub_check_btn": "🔄 I subscribed",
        "sub_fail": "❌ You haven't subscribed to all channels yet!",
        "sub_success": "✅ Subscription confirmed!",
        "help_admin_title": "📋 Available commands (Administrator):",
        "help_user_title": "📋 Available commands:",
        "cmd_start": "Start bot",
        "cmd_suggest": "Suggest file",
        "cmd_check_vt": "Check via VT",
        "cmd_help": "Command list",
        "cmd_add": "Add file to database",
        "cmd_edit": "Edit file by tag",
        "cmd_files": "Database file list",
        "cmd_search": "Search file",
        "cmd_del": "Delete file by tag",
        "cmd_links": "Subscription channels",
        "cmd_full": "Export all files",
        "cmd_stop": "Stop export",
        "cmd_db": "Download main database",
        "cmd_update_db": "Update description base",
        "cmd_stats_files": "File stats and ratings",
        "admin_no_rights": "❌ Insufficient rights.",
        "admin_add_prompt": "📤 Send a file, photo or video with tag and description (or ZIP archive for mass import):",
        "admin_edit_usage": "⚠️ Specify tag: `/edit tag`",
        "admin_edit_not_found": "❌ Tag not found in database.",
        "admin_edit_prompt": "✏️ Send new file for tag",
        "admin_db_not_found": "❌ db.txt not found in channel.",
        "admin_search_usage": "⚠️ Specify query: `/search query`",
        "admin_search_empty": "❌ Nothing found.",
        "admin_files_empty": "📭 File list is empty.",
        "admin_full_empty": "📭 Database is empty.",
        "admin_full_start": "📦 Starting export... Type /stop to cancel",
        "admin_full_stop": "🛑 Export cancelled.",
        "admin_full_done": "✅ Export completed!",
        "admin_saved": "✅ Saved tag:",
        "admin_updated": "✏️ File updated!",
        "vt_prompt": "🛡 Send a file or text link to check via VirusTotal:",
        "vt_checking_url": "🛡 Checking link via VirusTotal...",
        "vt_checking_file": "🛡 Checking file via VirusTotal...",
        "vt_success_url": "✅ Link checked!\n\n🔗 Report:",
        "vt_success_file": "✅ File successfully sent for check!\n\n🔗 Report:",
        "vt_already": "ℹ️ File is already in VirusTotal database!\n\n🔗 Report:",
        "suggest_prompt": "📤 Send a file, photo or video with tag and description in caption (e.g., `my_tag File description`):",
        "suggest_success": "✅ File successfully sent to administration for review!",
        "links_header": "🔗 **Required subscription channels:**\n\n",
        "links_usage": "⚠️ Usage:\n`/links add @channel` — add channel\n`/links del @channel` — remove channel",
        "links_added": "✅ Successfully added subscription channel:",
        "links_deleted": "🗑 Successfully removed subscription channel:",
        "db_empty": "📭 The database is empty.",
        "stats_title": "📊 **File ratings and moderation:**",
        "stats_row": "🔹 `#{tag}` | Downloads: {downloads} | Ratings: {ratings} | Average: ⭐ {avg}/5",
        "error_generic": "❌ Error: {error}",
        "db_updated": "✅ Database updated successfully! Descriptions checked and synced: {count}",
        "btn_prev": "⬅️ Previous",
        "btn_next": "Next ➡️",
        "files_list_title": "📂 File list (Page {page} of {total}):",
        "search_results_title": "🔍 Search results for '{query}':",
        "file_desc_line": "📝 Description: {desc}",
        "file_downloads_line": "📥 Downloads: {count}",
        "page_suffix": "(Page {page}/{total})",
        "full_tag_error": "⚠️ Failed to export tag {tag}: {error}",
        "uptime_fmt": "{d}d {h}h {m}m {s}s",
        "status_approved": "✅ APPROVED",
        "status_approved_edited": "✅ APPROVED & EDITED",
        "status_rejected": "❌ REJECTED",
        "status_rejected_reason": "❌ REJECTED: {reason}",
        "toast_approved": "Approved successfully!",
        "toast_rejected": "Rejected.",
        "suggest_approved_user": "✅ Your suggested file has been approved!",
        "suggest_rejected_user": "❌ Your suggested file was rejected.",
        "suggest_approved_link_user": "✅ Your suggestion was approved: {link}",
        "suggest_rejected_reason_user": "❌ Your suggestion was rejected.\nReason: {reason}",
        "edit_approve_prompt": "✏️ Enter a new tag and description separated by a space (e.g. `new_tag Description`):",
        "reject_reason_prompt": "💬 Enter the rejection reason:",
        "notify_new_available": "🚀 New file available!\n🔗 {link}\n📝 {desc}",
        "notify_new_added": "🚀 New file added!\n🔗 {link}\n📝 {desc}",
        "notify_updated": "🔄 File update available!\n🔗 {link}\n📝 {desc}",
        "file_deleted": "🗑 Deleted: {tag}",
        "link_exists": "⚠️ Channel {channel} is already in the list.",
        "link_cannot_delete": "⚠️ You can't delete the last channel, or the channel was not found.",
        "suggest_need_tag": "⚠️ Please specify a tag!",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "btn_edit_approve": "✏️ Edit & Approve",
        "btn_edit_reject": "✏️ Edit & Reject",
        "suggested_by": "Suggested by:",
        "vt_no_key": "⚠️ VT API key is not configured.",
        "vt_error": "❌ VirusTotal error: {error}",
        "vt_send_file_or_link": "⚠️ Please send a file or link.",
        "arg_tag": "tag",
        "arg_query": "query",
        "daily_stats_title": "📊 **Daily Bot Statistics**",
        "daily_stats_date": "📅 Date: {date}",
        "daily_stats_files": "📂 Total files: {count}",
        "daily_stats_downloads": "📥 Total downloads: {count}",
        "btn_files": "📂 Files",
        "files_menu_title": "📂 Choose a section:",
        "btn_new": "🆕 New",
        "btn_top": "🔥 Popular",
        "btn_rated": "⭐ Top rated",
        "btn_search": "🔍 Search",
        "list_title": "{name} · {page}/{total}",
        "pick_file": "👇 Choose a file:",
        "search_prompt": "🔍 Enter your search query:",
        "rating_line": "⭐ Rating: {avg}/5 ({n}) · 📥 {dl}",
        "btn_notify_on": "🔔 Notifications: on",
        "btn_notify_off": "🔕 Notifications: off",
        "notify_on_toast": "🔔 Notifications enabled",
        "notify_off_toast": "🔕 Notifications disabled",
        "flood_warn": "⏳ Slow down! Please wait a few seconds.",
        "banned_msg": "🚫 You have been blocked from using this bot.",
        "ban_usage": "⚠️ Usage: /ban ID or /unban ID",
        "ban_done": "🚫 User {uid} has been banned.",
        "unban_done": "✅ User {uid} has been unbanned.",
        "ban_admin": "⚠️ You can't ban the administrator.",
        "cmd_ban": "Ban a user",
        "cmd_unban": "Unban a user",
        "cmd_broadcast": "Broadcast to all users",
        "cmd_stats": "Overall bot statistics",
        "arg_id": "ID",
        "arg_text": "text",
        "broadcast_usage": "⚠️ Usage: /broadcast text",
        "broadcast_started": "📣 Broadcast started...",
        "broadcast_done": "📣 Broadcast finished. Sent: {ok}, failed: {fail}",
        "stats_overview": "📊 Bot statistics\n\n👥 Users: {users}\n🚫 Banned: {banned}\n📂 Files: {files}\n📥 Downloads: {downloads}\n\n🔥 Top 5:\n{top}",
        "btn_qr_code": "📷 QR Code",
        "qr_code_caption": "📷 QR Code for file `{tag}`:\n🔗 Link: {link}",
        "btn_achievements": "🏆 Achievements & Titles",
        "btn_select_title": "🎖 Select Title",
        "btn_clear_title": "❌ Remove Title",
        "title_equipped": "✅ Title equipped: {title}",
        "title_cleared": "🗑 Title removed!",
        "select_title_prompt": "🎖 Choose a title from your unlocked achievements (displayed in /start):",
        "no_titles_unlocked": "🔒 You have no unlocked titles yet. Download files, invite friends, or suggest content!",
        "ref_menu_title": "🏆 <b>Achievements & Referrals</b>\n\n🔗 Your referral link:\n<code>{ref_link}</code>\n\n👥 Friends: <b>{ref_count}</b> | 📥 Downloads: <b>{dl_count}</b>\n⭐ Ratings: <b>{rate_count}</b> | 📤 Approved files: <b>{sug_count}</b>\n🎖 Active Title: <b>{cur_title}</b>\n\n📜 <b>Titles list:</b>\n{achievements}",
        "zip_upload_start": "📦 Unpacking ZIP archive and importing files...",
        "zip_upload_done": "✅ Successfully imported files from archive: {count}",
        "zip_error": "❌ ZIP archive processing error: {error}",
        "title_dl_1": "Newbie",
        "title_dl_5": "In The Loop",
        "title_dl_10": "Seeker",
        "title_dl_20": "File Crush",
        "title_dl_50": "Cyber Hunter",
        "title_dl_67": "Six Seven",
        "title_dl_100": "First Champion",
        "title_dl_200": "Cyber Machine",
        "title_dl_228": "Underground Legend",
        "title_dl_500": "Traffic Overlord",
        "title_dl_1000": "Database Architect",
        "title_dl_1337": "Elite Hax0r",
        "title_dl_1488": "Absolute Boss",
        "title_ref_1": "Pathfinder",
        "title_ref_5": "Life of the Party",
        "title_ref_10": "Squad Leader",
        "title_ref_20": "Ambassador",
        "title_ref_50": "Influencer",
        "title_ref_67": "Six Seven Squad",
        "title_ref_100": "Community Tycoon",
        "title_rate_1": "First Look",
        "title_rate_10": "True Critic",
        "title_rate_25": "Chief Inspector",
        "title_sug_1": "Helper",
        "title_sug_5": "Goods Supplier",
        "title_sug_15": "Channel Patron",
        "title_admin_god": "👑 Head Admin",
        "desc_dl_1": "1 download",
        "desc_dl_5": "5 downloads",
        "desc_dl_10": "10 downloads",
        "desc_dl_20": "20 downloads",
        "desc_dl_50": "50 downloads",
        "desc_dl_67": "67 downloads",
        "desc_dl_100": "100 downloads",
        "desc_dl_200": "200 downloads",
        "desc_dl_228": "228 downloads",
        "desc_dl_500": "1000 downloads",
        "desc_dl_1000": "1000 downloads",
        "desc_dl_1337": "1337 downloads",
        "desc_dl_1488": "1488 downloads",
        "desc_ref_1": "1 friend",
        "desc_ref_5": "5 friends",
        "desc_ref_10": "10 friends",
        "desc_ref_20": "20 friends",
        "desc_ref_50": "50 friends",
        "desc_ref_67": "67 friends",
        "desc_ref_100": "100 friends",
        "desc_rate_1": "1 rating",
        "desc_rate_10": "10 ratings",
        "desc_rate_25": "25 ratings",
        "desc_sug_1": "1 approved file",
        "desc_sug_5": "5 approved files",
        "desc_sug_15": "15 approved files",
        "desc_admin_god": "Special administrator status"
    },
    "ja": {
        "lang_name": "🇯🇵 日本語",
        "welcome": "👋 こんにちは、{name}{title_part}！\n\n💬 @goat1488_67 のファイルマネージャーです！\n\n🔽 下のボタンを使って移動してください",
        "btn_channel": "📢 チャンネル",
        "btn_profile": "⚙️ プロフィール",
        "btn_feedback": "👤 フィードバック",
        "btn_suggest": "📤 ファイルを提案",
        "btn_commands": "📋 コマンド",
        "btn_lang": "🌐 言語: 日本語",
        "select_lang": "言語を選択してください / Choose language:",
        "lang_set": "✅ 言語が変更されました！",
        "profile_title": "👤 プロフィール",
        "profile_id": "🆔 ID",
        "profile_name": "👤 名前",
        "profile_title_line": "🎖 称号",
        "no_title": "未設定",
        "profile_username": "👤 ユーザー名",
        "profile_uptime": "⏳ 稼働時間",
        "profile_my_dl": "📥 あなたのダウンロード数",
        "profile_total_dl": "📥 ボットの総ダウンロード数",
        "profile_fav_count": "⭐ お気に入りファイル数",
        "btn_favorites": "⭐ お気に入り",
        "btn_fav_add": "⭐ お気に入りに追加",
        "btn_fav_del": "🗑 お気に入りから削除",
        "fav_added": "✅ お気に入りに追加しました！",
        "fav_removed": "🗑 お気に入りから削除しました！",
        "favorites_title": "⭐ **お気に入り一覧:**",
        "favorites_empty": "📭 お気に入りリストは空です。",
        "back": "🔙 戻る",
        "rate_thanks": "⭐ 評価ありがとうございます: ",
        "rate_prompt": "ファイルを評価するか、報告を送信してください:",
        "report_btn": "🚨 ファイルを報告",
        "report_title": "🚨 **ファイル報告**",
        "report_tag": "🔗 タグ",
        "report_reason": "📋 理由",
        "report_user": "👤 ユーザーから",
        "report_success": "✅ 管理者に報告が正常に送信されました！",
        "reason_virus": "🦠 ウイルスが含まれています",
        "reason_outdated": "🔄 古いバージョン",
        "reason_broken": "🚫 壊れたファイル",
        "reason_other": "❌ その他の理由",
        "file_not_found": "❌ ファイルが見つかりません。",
        "sub_required": "❌ ファイルを受け取るには、チャンネルを購読する必要があります：",
        "sub_btn": "📢 チャンネル登録 ",
        "sub_check_btn": "🔄 登録しました",
        "sub_fail": "❌ まだすべてのチャンネルに登録していません！",
        "sub_success": "✅ 登録が確認されました！",
        "help_admin_title": "📋 利用可能なコマンド (管理者):",
        "help_user_title": "📋 利用可能なコマンド:",
        "cmd_start": "ボット起動",
        "cmd_suggest": "ファイル提案",
        "cmd_check_vt": "VT確認",
        "cmd_help": "コマンド一覧",
        "cmd_add": "追加",
        "cmd_edit": "編集",
        "cmd_files": "ファイル一覧",
        "cmd_search": "検索",
        "cmd_del": "削除",
        "cmd_links": "チャンネル",
        "cmd_full": "エクスポート",
        "cmd_stop": "停止",
        "cmd_db": "DB取得",
        "cmd_update_db": "更新",
        "cmd_stats_files": "統計",
        "admin_no_rights": "❌ 権限がありません。",
        "admin_add_prompt": "📤 キャプションにタグと説明を入れてファイル、写真、動画を送信してください:",
        "admin_edit_usage": "⚠️ タグを指定してください: `/edit tag`",
        "admin_edit_not_found": "❌ データベースにタグが見つかりません。",
        "admin_edit_prompt": "✏️ タグ用の新しいファイルを送信してください",
        "admin_db_not_found": "❌ チャンネルに db.txt が見つかりません。",
        "admin_search_usage": "⚠️ 検索クエリを指定してください: `/search クエリ`",
        "admin_search_empty": "❌ 何も見つかりませんでした。",
        "admin_files_empty": "📭 ファイルリストは空です。",
        "admin_full_empty": "📭 データベースは空です。",
        "admin_full_start": "📦 エクスポート中... キャンセルするには /stop",
        "admin_full_stop": "🛑 エクスポートがキャンセルされました。",
        "admin_full_done": "✅ エクスポート完了！",
        "admin_saved": "✅ タグを保存しました:",
        "admin_updated": "✏️ ファイルを更新しました！",
        "vt_prompt": "🛡 VirusTotalで確認するファイルまたはリンクを送信してください:",
        "vt_checking_url": "🛡 VirusTotalでリンクを確認中...",
        "vt_checking_file": "🛡 VirusTotalでファイルを確認中...",
        "vt_success_url": "✅ リンクを確認しました！\n\n🔗 レポート:",
        "vt_success_file": "✅ ファイルの確認が正常に送信されました！\n\n🔗 レポート:",
        "vt_already": "ℹ️ ファイルはすでにVirusTotalデータベースに存在します！\n\n🔗 レポート:",
        "suggest_prompt": "📤 キャプションにタグと説明を入れてファイル、写真、動画を送信してください (例: `my_tag ファイルの説明`):",
        "suggest_success": "✅ ファイルが審査のために管理者に正常に送信されました！",
        "links_header": "🔗 **必須チャンネル登録:**\n\n",
        "links_usage": "⚠️ 使用方法:\n`/links add @channel` — チャンネルを追加\n`/links del @channel` — チャンネルを削除",
        "links_added": "✅ チャンネルが正常に追加されました:",
        "links_deleted": "🗑 チャンネルが正常に削除されました:",
        "db_empty": "📭 データベースは空です。",
        "stats_title": "📊 **ファイルの評価とモデレーション:**",
        "stats_row": "🔹 `#{tag}` | ダウンロード数: {downloads} | 評価数: {ratings} | 平均: ⭐ {avg}/5",
        "error_generic": "❌ エラー: {error}",
        "db_updated": "✅ データベースを更新しました！確認・同期した説明の数: {count}",
        "btn_prev": "⬅️ 前へ",
        "btn_next": "次へ ➡️",
        "files_list_title": "📂 ファイル一覧（{page}/{total} ページ）:",
        "search_results_title": "🔍 「{query}」の検索結果:",
        "file_desc_line": "📝 説明: {desc}",
        "file_downloads_line": "📥 ダウンロード数: {count}",
        "page_suffix": "（{page}/{total} ページ）",
        "full_tag_error": "⚠️ タグ {tag} のエクスポートに失敗しました: {error}",
        "uptime_fmt": "{d}日 {h}時間 {m}分 {s}秒",
        "status_approved": "✅ 承認済み",
        "status_approved_edited": "✅ 編集して承認済み",
        "status_rejected": "❌ 却下済み",
        "status_rejected_reason": "❌ 却下済み: {reason}",
        "toast_approved": "承認しました！",
        "toast_rejected": "却下しました。",
        "suggest_approved_user": "✅ 提案されたファイルが承認されました！",
        "suggest_rejected_user": "❌ 提案されたファイルは却下されました。",
        "suggest_approved_link_user": "✅ 提案が承認されました: {link}",
        "suggest_rejected_reason_user": "❌ 提案は却下されました。\n理由: {reason}",
        "edit_approve_prompt": "✏️ 新しいタグと説明をスペースで区切って入力してください（例: `new_tag 説明`）:",
        "reject_reason_prompt": "💬 却下の理由を入力してください:",
        "notify_new_available": "🚀 新しいファイルが利用可能です！\n🔗 {link}\n📝 {desc}",
        "notify_new_added": "🚀 新しいファイルが追加されました！\n🔗 {link}\n📝 {desc}",
        "notify_updated": "🔄 ファイルの更新があります！\n🔗 {link}\n📝 {desc}",
        "file_deleted": "🗑 削除しました: {tag}",
        "link_exists": "⚠️ チャンネル {channel} は既にリストにあります。",
        "link_cannot_delete": "⚠️ 最後のチャンネルは削除できません。またはチャンネルが見つかりません。",
        "suggest_need_tag": "⚠️ タグを指定してください！",
        "btn_approve": "✅ 承認",
        "btn_reject": "❌ 却下",
        "btn_edit_approve": "✏️ 編集して承認",
        "btn_edit_reject": "✏️ 編集して却下",
        "suggested_by": "提案者:",
        "vt_no_key": "⚠️ VT APIキーが設定されていません。",
        "vt_error": "❌ VirusTotalエラー: {error}",
        "vt_send_file_or_link": "⚠️ ファイルまたはリンクを送信してください。",
        "arg_tag": "タグ",
        "arg_query": "検索語",
        "daily_stats_title": "📊 **ボットの毎日の統計**",
        "daily_stats_date": "📅 日付: {date}",
        "daily_stats_files": "📂 ファイル総数: {count}",
        "daily_stats_downloads": "📥 ダウンロード総数: {count}",
        "btn_files": "📂 ファイル",
        "files_menu_title": "📂 セクションを選んでください:",
        "btn_new": "🆕 新着",
        "btn_top": "🔥 人気",
        "btn_rated": "⭐ 高評価",
        "btn_search": "🔍 検索",
        "list_title": "{name} · {page}/{total}",
        "pick_file": "👇 ファイルを選んでください:",
        "search_prompt": "🔍 検索ワードを入力してください:",
        "rating_line": "⭐ 評価: {avg}/5（{n}件）· 📥 {dl}",
        "btn_notify_on": "🔔 通知: オン",
        "btn_notify_off": "🔕 通知: オフ",
        "notify_on_toast": "🔔 通知をオンにしました",
        "notify_off_toast": "🔕 通知をオフにしました",
        "flood_warn": "⏳ ゆっくりお願いします。数秒お待ちください。",
        "banned_msg": "🚫 このボットの利用が制限されています。",
        "ban_usage": "⚠️ 使い方: /ban ID または /unban ID",
        "ban_done": "🚫 ユーザー {uid} をブロックしました。",
        "unban_done": "✅ ユーザー {uid} のブロックを解除しました。",
        "ban_admin": "⚠️ 管理者はブロックできません。",
        "cmd_ban": "ユーザーをブロック",
        "cmd_unban": "ブロック解除",
        "cmd_broadcast": "全ユーザーに配信",
        "cmd_stats": "ボット全体の統計",
        "arg_id": "ID",
        "arg_text": "テキスト",
        "broadcast_usage": "⚠️ 使い方: /broadcast テキスト",
        "broadcast_started": "📣 配信を開始しました...",
        "broadcast_done": "📣 配信が完了しました。送信: {ok}、失敗: {fail}",
        "stats_overview": "📊 ボット統計\n\n👥 ユーザー数: {users}\n🚫 ブロック中: {banned}\n📂 ファイル数: {files}\n📥 ダウンロード数: {downloads}\n\n🔥 トップ5:\n{top}",
        "btn_qr_code": "📷 QRコード",
        "qr_code_caption": "📷 ファイル `{tag}` のQRコード:\n🔗 リンク: {link}",
        "btn_achievements": "🏆 実績と称号",
        "btn_select_title": "🎖 称号を選択",
        "btn_clear_title": "❌ 称号を外す",
        "title_equipped": "✅ 称号を設定しました: {title}",
        "title_cleared": "🗑 称号を外しました！",
        "select_title_prompt": "🎖 解除済みの実績から称号を選択してください（/start で表示されます）:",
        "no_titles_unlocked": "🔒 まだ解除された称号がありません。ファイルをダウンロードしたり、友達を招待したりしよう！",
        "ref_menu_title": "🏆 <b>実績と紹介</b>\n\n🔗 あなたの紹介リンク:\n<code>{ref_link}</code>\n\n👥 友達: <b>{ref_count}</b> | 📥 DL数: <b>{dl_count}</b>\n⭐ 評価数: <b>{rate_count}</b> | 📤 承認ファイル: <b>{sug_count}</b>\n🎖 現在の称号: <b>{cur_title}</b>\n\n📜 <b>称号リスト:</b>\n{achievements}",
        "zip_upload_start": "📦 ZIPアーカイブを解凍してデータベースに一括インポートしています...",
        "zip_upload_done": "✅ アーカイブから正常にインポートされたファイル数: {count}",
        "zip_error": "❌ ZIPアーカイブ処理エラー: {error}",
        "title_dl_1": "初心者",
        "title_dl_5": "通なユーザー",
        "title_dl_10": "シーカー",
        "title_dl_20": "ファイル推し",
        "title_dl_50": "サイバーハンター",
        "title_dl_67": "Six Seven",
        "title_dl_100": "初代チャンピオン",
        "title_dl_200": "サイバーマシン",
        "title_dl_228": "アンダーグラウンド伝説",
        "title_dl_500": "トラフィックの覇王",
        "title_dl_1000": "DBアーキテクト",
        "title_dl_1337": "Elite Hax0r",
        "title_dl_1488": "絶対的ボス",
        "title_ref_1": "案内人",
        "title_ref_5": "ムードメーカー",
        "title_ref_10": "スクワッドリーダー",
        "title_ref_20": "アンバサダー",
        "title_ref_50": "インフルエンサー",
        "title_ref_67": "Six Seven Squad",
        "title_ref_100": "コミュニティ王",
        "title_rate_1": "ファーストルック",
        "title_rate_10": "真の批評家",
        "title_rate_25": "主任査察官",
        "title_sug_1": "ヘルパー",
        "title_sug_5": "神ファイル提供者",
        "title_sug_15": "チャンネルのパトロン",
        "title_admin_god": "👑 ヘッドアドミン",
        "desc_dl_1": "1 DL",
        "desc_dl_5": "5 DL",
        "desc_dl_10": "10 DL",
        "desc_dl_20": "20 DL",
        "desc_dl_50": "50 DL",
        "desc_dl_67": "67 DL",
        "desc_dl_100": "100 DL",
        "desc_dl_200": "200 DL",
        "desc_dl_228": "228 DL",
        "desc_dl_500": "1000 DL",
        "desc_dl_1000": "1000 DL",
        "desc_dl_1337": "1337 DL",
        "desc_dl_1488": "1488 DL",
        "desc_ref_1": "友達1人",
        "desc_ref_5": "友達5人",
        "desc_ref_10": "友達10人",
        "desc_ref_20": "友達20人",
        "desc_ref_50": "友達50人",
        "desc_ref_67": "友達67人",
        "desc_ref_100": "友達100人",
        "desc_rate_1": "評価1回",
        "desc_rate_10": "評価10回",
        "desc_rate_25": "評価25回",
        "desc_sug_1": "承認1件",
        "desc_sug_5": "承認5件",
        "desc_sug_15": "承認15件",
        "desc_admin_god": "特別管理者ステータス"
    }
}

def get_text(user_id, key, mapping):
    lang = mapping.get("_users_lang", {}).get(str(user_id), "uk")
    return LANGS.get(lang, LANGS["uk"]).get(key, LANGS["uk"].get(key, key))

def get_user_metrics(user_id, mapping):
    uid_str = str(user_id)
    user_key = f"dl_user_{user_id}"
    dl_count = sum(item.get(user_key, 0) for k, item in mapping.items() if not k.startswith("_") and isinstance(item, dict))
    ref_count = len(mapping.get("_referrals", {}).get(uid_str, []))
    
    rate_count = 0
    for k, item in mapping.items():
        if not k.startswith("_") and isinstance(item, dict):
            for r in item.get("ratings", []):
                if r.get("user_id") == user_id:
                    rate_count += 1
                    
    sug_count = mapping.get("_approved_suggests", {}).get(uid_str, 0)
    admin_flag = 1 if user_id == ADMIN_ID else 0
    return dl_count, ref_count, rate_count, sug_count, admin_flag

def check_user_achievements(user_id, mapping):
    if "_achievements" not in mapping:
        mapping["_achievements"] = {}
    uid_str = str(user_id)
    user_achs = mapping["_achievements"].setdefault(uid_str, [])
    
    dl_count, ref_count, rate_count, sug_count, admin_flag = get_user_metrics(user_id, mapping)
    metrics_map = {
        "dl": dl_count,
        "ref": ref_count,
        "rate": rate_count,
        "sug": sug_count,
        "admin": admin_flag
    }
    
    changed = False
    for ach_id, cat, req in ACHIEVEMENTS_CONFIG:
        if metrics_map.get(cat, 0) >= req and ach_id not in user_achs:
            user_achs.append(ach_id)
            changed = True
            
    return user_achs, changed

def get_active_title_str(user_id, mapping):
    uid_str = str(user_id)
    ach_id = mapping.get("_active_title", {}).get(uid_str)
    if not ach_id:
        return ""
    user_achs, _ = check_user_achievements(user_id, mapping)
    if ach_id not in user_achs:
        return ""
    return get_text(user_id, f"title_{ach_id}", mapping)

def file_button(tag, data, bot_username, suffix=""):
    desc = (data.get("desc") or "").strip().split("\n")[0]
    title = f"{tag} — {desc}" if desc else tag
    if len(title) > 34:
        title = title[:33] + "…"
    label = f"📄 {title}{suffix}"
    cb = f"getfile_{tag}"
    if len(cb.encode("utf-8")) <= 64:
        return InlineKeyboardButton(label, callback_data=cb)
    return InlineKeyboardButton(label, url=f"https://t.me/{bot_username}?start={tag}")

def get_avg_rating(data):
    r = data.get("ratings") or []
    if not r:
        return 0.0, 0
    return sum(x.get("stars", 0) for x in r) / len(r), len(r)

def get_sorted_files(mapping, mode):
    files = [(t, d) for t, d in mapping.items() if not t.startswith("_") and isinstance(d, dict)]
    if mode == "top":
        files.sort(key=lambda x: x[1].get("downloads", 0), reverse=True)
    elif mode == "rated":
        files = [f for f in files if f[1].get("ratings")]
        files.sort(key=lambda x: get_avg_rating(x[1]), reverse=True)
    else:
        files.sort(key=lambda x: x[1].get("msg_id", 0), reverse=True)
    return files

def list_suffix(mode, data):
    if mode == "top":
        return f" · 📥{data.get('downloads', 0)}"
    if mode == "rated":
        return f" · ⭐{get_avg_rating(data)[0]:.1f}"
    return ""

def search_files(mapping, query):
    q = query.lower()
    found = [(t, d) for t, d in mapping.items()
             if not t.startswith("_") and isinstance(d, dict) and (q in t.lower() or q in (d.get("desc") or "").lower())]
    found.sort(key=lambda x: x[1].get("downloads", 0), reverse=True)
    return found

def send_search_results(chat_id, user_id, query, mapping):
    found = search_files(mapping, query)
    if not found:
        bot.send_message(chat_id, get_text(user_id, "admin_search_empty", mapping))
        return
    bot_username = bot.get_me().username
    markup = InlineKeyboardMarkup(row_width=1)
    for tag, data in found[:10]:
        markup.add(file_button(tag, data, bot_username))
    bot.send_message(chat_id, get_text(user_id, "search_results_title", mapping).format(query=query), reply_markup=markup)

FLOOD_LIMIT = 8
FLOOD_WINDOW = 10
user_actions = {}

def flood_status(user_id):
    if user_id == ADMIN_ID:
        return 0
    now = time.time()
    q = [t for t in user_actions.get(user_id, []) if now - t < FLOOD_WINDOW]
    q.append(now)
    user_actions[user_id] = q
    if len(q) <= FLOOD_LIMIT:
        return 0
    return 1 if len(q) == FLOOD_LIMIT + 1 else 2

def is_banned(user_id, mapping):
    return str(user_id) in mapping.get("_banned", [])

def guard_message(message, mapping):
    uid = message.from_user.id
    if uid == ADMIN_ID:
        return False
    if is_banned(uid, mapping):
        bot.send_message(message.chat.id, get_text(uid, "banned_msg", mapping))
        return True
    st = flood_status(uid)
    if st == 1:
        bot.send_message(message.chat.id, get_text(uid, "flood_warn", mapping))
    return st != 0

def set_user_commands(user_id, is_admin, mapping):
    try:
        if is_admin:
            commands = [
                BotCommand("start", get_text(user_id, "cmd_start", mapping)),
                BotCommand("add", get_text(user_id, "cmd_add", mapping)),
                BotCommand("edit", get_text(user_id, "cmd_edit", mapping)),
                BotCommand("files", get_text(user_id, "cmd_files", mapping)),
                BotCommand("search", get_text(user_id, "cmd_search", mapping)),
                BotCommand("del", get_text(user_id, "cmd_del", mapping)),
                BotCommand("stats", get_text(user_id, "cmd_stats", mapping)),
                BotCommand("ban", get_text(user_id, "cmd_ban", mapping)),
                BotCommand("unban", get_text(user_id, "cmd_unban", mapping)),
                BotCommand("broadcast", get_text(user_id, "cmd_broadcast", mapping)),
                BotCommand("links", get_text(user_id, "cmd_links", mapping)),
                BotCommand("full", get_text(user_id, "cmd_full", mapping)),
                BotCommand("stop", get_text(user_id, "cmd_stop", mapping)),
                BotCommand("db", get_text(user_id, "cmd_db", mapping)),
                BotCommand("update_db", get_text(user_id, "cmd_update_db", mapping)),
                BotCommand("stats_files", get_text(user_id, "cmd_stats_files", mapping)),
                BotCommand("suggest", get_text(user_id, "cmd_suggest", mapping)),
                BotCommand("check_vt", get_text(user_id, "cmd_check_vt", mapping)),
                BotCommand("help", get_text(user_id, "cmd_help", mapping)),
            ]
        else:
            commands = [
                BotCommand("start", get_text(user_id, "cmd_start", mapping)),
                BotCommand("search", get_text(user_id, "cmd_search", mapping)),
                BotCommand("suggest", get_text(user_id, "cmd_suggest", mapping)),
                BotCommand("check_vt", get_text(user_id, "cmd_check_vt", mapping)),
                BotCommand("help", get_text(user_id, "cmd_help", mapping)),
            ]
        bot.set_my_commands(commands, scope=telebot.types.BotCommandScopeChat(chat_id=user_id))
    except Exception as e:
        print(f"Помилка встановлення команд для {user_id}: {e}")

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
        print(f"Не вдалося підвантажити базу з каналу: {e}")
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
        print(f"Помилка збереження бази в канал: {e}")

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
            print(f"Не вдалося перевірити підписку на {ch}: {e}")
    return not_subbed

def get_sub_keyboard(not_subbed, file_key, user_id, mapping):
    markup = InlineKeyboardMarkup(row_width=1)
    sub_text = get_text(user_id, "sub_btn", mapping)
    check_text = get_text(user_id, "sub_check_btn", mapping)
    for ch in not_subbed:
        clean_ch = ch.replace("@", "")
        markup.add(InlineKeyboardButton(f"{sub_text}{ch}", url=f"https://t.me/{clean_ch}"))
    markup.add(InlineKeyboardButton(check_text, callback_data=f"sub_check_{file_key}"))
    return markup

def get_start_keyboard(user_id, mapping):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_channel = InlineKeyboardButton(get_text(user_id, "btn_channel", mapping), url="https://t.me/goat1488_67")
    btn_profile = InlineKeyboardButton(get_text(user_id, "btn_profile", mapping), callback_data="open_profile")
    btn_feedback = InlineKeyboardButton(get_text(user_id, "btn_feedback", mapping), url=FEEDBACK_BOT_URL)
    btn_suggest = InlineKeyboardButton(get_text(user_id, "btn_suggest", mapping), callback_data="click_suggest")
    btn_commands = InlineKeyboardButton(get_text(user_id, "btn_commands", mapping), callback_data="click_commands")
    btn_files = InlineKeyboardButton(get_text(user_id, "btn_files", mapping), callback_data="open_files")
    btn_lang = InlineKeyboardButton(get_text(user_id, "btn_lang", mapping), callback_data="change_lang")
    
    markup.add(btn_channel, btn_profile)
    markup.add(btn_feedback, btn_suggest)
    markup.add(btn_files, btn_commands)
    markup.add(btn_lang)
    return markup

def get_profile_keyboard(user_id, mapping):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_favs = InlineKeyboardButton(get_text(user_id, "btn_favorites", mapping), callback_data="open_favorites_1")
    btn_ach = InlineKeyboardButton(get_text(user_id, "btn_achievements", mapping), callback_data="open_achievements")
    btn_back = InlineKeyboardButton(get_text(user_id, "back", mapping), callback_data="back_to_main")
    notify_on = str(user_id) not in mapping.get("_notify_off", [])
    btn_notify = InlineKeyboardButton(get_text(user_id, "btn_notify_on" if notify_on else "btn_notify_off", mapping), callback_data="toggle_notify")
    markup.add(btn_favs, btn_ach)
    markup.add(btn_notify)
    markup.add(btn_back)
    return markup

def get_lang_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    for code, data in LANGS.items():
        markup.add(InlineKeyboardButton(data["lang_name"], callback_data=f"setlang_{code}"))
    return markup

def format_welcome_text(user, mapping):
    active_title = get_active_title_str(user.id, mapping)
    title_part = f" ({active_title})" if active_title else ""
    first_name = user.first_name or "User"
    return get_text(user.id, "welcome", mapping).format(name=first_name, title_part=title_part)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user = message.from_user
    is_admin = (user.id == ADMIN_ID)
    mapping = load_mapping()
    if guard_message(message, mapping):
        return

    if "_users_lang" not in mapping:
        mapping["_users_lang"] = {}
    
    if str(user.id) not in mapping["_users_lang"] and len(message.text.split()) <= 1:
        user_lang = user.language_code if user and user.language_code else "uk"
        if user_lang not in LANGS:
            user_lang = "uk"
        mapping["_users_lang"][str(user.id)] = user_lang
        save_mapping_data(mapping)

    set_user_commands(user.id, is_admin, mapping)

    if user.id == ADMIN_ID:
        _, changed = check_user_achievements(user.id, mapping)
        if changed:
            save_mapping_data(mapping)

    args = message.text.split()
    if len(args) > 1:
        arg_val = args[1]
        if arg_val.startswith("ref_"):
            ref_owner = arg_val.replace("ref_", "")
            if ref_owner.isdigit() and int(ref_owner) != user.id:
                if "_referrals" not in mapping:
                    mapping["_referrals"] = {}
                user_refs = mapping["_referrals"].setdefault(ref_owner, [])
                if user.id not in user_refs:
                    user_refs.append(user.id)
                    check_user_achievements(int(ref_owner), mapping)
                    save_mapping_data(mapping)
        else:
            file_key = arg_val
            not_subbed = check_user_subscriptions(user.id, mapping)
            if not_subbed:
                bot.send_message(
                    message.chat.id,
                    get_text(user.id, "sub_required", mapping),
                    reply_markup=get_sub_keyboard(not_subbed, file_key, user.id, mapping)
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
                
                check_user_achievements(user.id, mapping)
                save_mapping_data(mapping)
                send_file_to_user(message.chat.id, file_key, user.id, mapping)
            else:
                bot.send_message(message.chat.id, get_text(user.id, "file_not_found", mapping))
            return

    caption_text = format_welcome_text(user, mapping)
    try:
        with open("1.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption_text, reply_markup=get_start_keyboard(user.id, mapping))
    except Exception:
        bot.send_message(message.chat.id, caption_text, reply_markup=get_start_keyboard(user.id, mapping))

@bot.message_handler(commands=["stats_files"])
def stats_files_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    mapping = load_mapping()
    files_only = {k: v for k, v in mapping.items() if not k.startswith("_")}
    
    if not files_only:
        bot.send_message(message.chat.id, get_text(message.from_user.id, "db_empty", mapping))
        return

    text = get_text(message.from_user.id, "stats_title", mapping) + "\n\n"
    for tag, data in files_only.items():
        ratings = data.get("ratings", [])
        avg_rating = sum(r["stars"] for r in ratings) / len(ratings) if ratings else 0.0
        downloads = data.get("downloads", 0)
        text += get_text(message.from_user.id, "stats_row", mapping).format(tag=tag, downloads=downloads, ratings=len(ratings), avg=f"{avg_rating:.1f}") + "\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def help_cmd(message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    mapping = load_mapping()
    
    if is_admin:
        text = (
            f"{get_text(user_id, 'help_admin_title', mapping)}\n\n"
            f"/start — {get_text(user_id, 'cmd_start', mapping)}\n"
            f"/add — {get_text(user_id, 'cmd_add', mapping)}\n"
            f"/edit [{get_text(user_id, 'arg_tag', mapping)}] — {get_text(user_id, 'cmd_edit', mapping)}\n"
            f"/del [{get_text(user_id, 'arg_tag', mapping)}] — {get_text(user_id, 'cmd_del', mapping)}\n"
            f"/stats — {get_text(user_id, 'cmd_stats', mapping)}\n"
            f"/ban [{get_text(user_id, 'arg_id', mapping)}] — {get_text(user_id, 'cmd_ban', mapping)}\n"
            f"/unban [{get_text(user_id, 'arg_id', mapping)}] — {get_text(user_id, 'cmd_unban', mapping)}\n"
            f"/broadcast [{get_text(user_id, 'arg_text', mapping)}] — {get_text(user_id, 'cmd_broadcast', mapping)}\n"
            f"/files — {get_text(user_id, 'cmd_files', mapping)}\n"
            f"/search [{get_text(user_id, 'arg_query', mapping)}] — {get_text(user_id, 'cmd_search', mapping)}\n"
            f"/full — {get_text(user_id, 'cmd_full', mapping)}\n"
            f"/stop — {get_text(user_id, 'cmd_stop', mapping)}\n"
            f"/db — {get_text(user_id, 'cmd_db', mapping)}\n"
            f"/update_db — {get_text(user_id, 'cmd_update_db', mapping)}\n"
            f"/stats_files — {get_text(user_id, 'cmd_stats_files', mapping)}\n"
            f"/links — {get_text(user_id, 'cmd_links', mapping)}\n"
            f"/suggest — {get_text(user_id, 'cmd_suggest', mapping)}\n"
            f"/check_vt — {get_text(user_id, 'cmd_check_vt', mapping)}\n"
            f"/help — {get_text(user_id, 'cmd_help', mapping)}"
        )
    else:
        text = (
            f"{get_text(user_id, 'help_user_title', mapping)}\n\n"
            f"/start — {get_text(user_id, 'cmd_start', mapping)}\n"
            f"/search [{get_text(user_id, 'arg_query', mapping)}] — {get_text(user_id, 'cmd_search', mapping)}\n"
            f"/suggest — {get_text(user_id, 'cmd_suggest', mapping)}\n"
            f"/check_vt — {get_text(user_id, 'cmd_check_vt', mapping)}\n"
            f"/help — {get_text(user_id, 'cmd_help', mapping)}"
        )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["db"])
def send_database_txt(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
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
        bot.send_message(message.chat.id, get_text(user_id, "admin_db_not_found", mapping))
    except Exception as e:
        bot.send_message(message.chat.id, get_text(user_id, "error_generic", mapping).format(error=e))

@bot.message_handler(commands=["suggest"])
def suggest_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if guard_message(message, mapping):
        return
    admin_states[user_id] = {"action": "suggest_file"}
    bot.send_message(message.chat.id, get_text(user_id, "suggest_prompt", mapping))

@bot.message_handler(commands=["check_vt"])
def check_vt_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if guard_message(message, mapping):
        return
    admin_states[user_id] = {"action": "check_vt_file"}
    bot.send_message(message.chat.id, get_text(user_id, "vt_prompt", mapping))

@bot.message_handler(commands=["update_db"])
def update_database_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    mapping = load_mapping()
    updated_count = 0
    
    for tag, data in mapping.items():
        if tag.startswith("_"):
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
                print(f"Помилка перевірки повідомлення {msg_id} для тега {tag}: {e}")
                
    save_mapping_data(mapping)
    bot.send_message(message.chat.id, get_text(message.from_user.id, "db_updated", mapping).format(count=updated_count))

def get_files_page_keyboard(page, total_pages, search_query="", user_id=ADMIN_ID, mapping=None):
    mapping = mapping or {}
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(get_text(user_id, "btn_prev", mapping), callback_data=f"files_page_{page-1}_{search_query}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(get_text(user_id, "btn_next", mapping), callback_data=f"files_page_{page+1}_{search_query}"))
        
    if buttons:
        markup.add(*buttons)
    return markup

def show_files_page(chat_id, message_id, page=1, search_query="", user_id=ADMIN_ID):
    mapping = load_mapping()
    files_only = {k: v for k, v in mapping.items() if not k.startswith("_")}

    if search_query:
        files_only = {k: v for k, v in files_only.items() if search_query.lower() in k.lower() or search_query.lower() in v.get("desc", "").lower()}

    if not files_only:
        text = get_text(user_id, "admin_files_empty", mapping)
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
    text = get_text(user_id, "files_list_title", mapping).format(page=page, total=total_pages) + "\n\n"
    
    for tag in current_keys:
        data = files_only[tag]
        link = f"https://t.me/{bot_username}?start={tag}"
        desc = data.get("desc", "")
        downloads = data.get("downloads", 0)
        text += f"🔗 {link}\n"
        if desc:
            text += get_text(user_id, "file_desc_line", mapping).format(desc=desc) + "\n"
        text += get_text(user_id, "file_downloads_line", mapping).format(count=downloads) + "\n\n"

    markup = get_files_page_keyboard(page, total_pages, search_query, user_id, mapping)
    
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, disable_web_page_preview=True)
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup, disable_web_page_preview=True)

@bot.message_handler(commands=["files"])
def list_files_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    show_files_page(message.chat.id, message.message_id, page=1, user_id=user_id)

@bot.message_handler(commands=["search"])
def search_file_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if guard_message(message, mapping):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        admin_states[user_id] = {"action": "user_search"}
        bot.send_message(message.chat.id, get_text(user_id, "search_prompt", mapping))
        return
    send_search_results(message.chat.id, user_id, args[1].strip(), mapping)

@bot.message_handler(commands=["stop"])
def stop_process_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    active_processes[ADMIN_ID] = False
    mapping = load_mapping()
    bot.send_message(message.chat.id, get_text(message.from_user.id, "admin_full_stop", mapping))

@bot.message_handler(commands=["full"])
def full_backup_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    
    files_only = {k: v for k, v in mapping.items() if not k.startswith("_")}
    
    if not files_only:
        bot.send_message(message.chat.id, get_text(user_id, "admin_full_empty", mapping))
        return
    
    active_processes[ADMIN_ID] = True
    bot.send_message(message.chat.id, get_text(user_id, "admin_full_start", mapping))
    
    for tag, data in files_only.items():
        if not active_processes.get(ADMIN_ID, True):
            bot.send_message(message.chat.id, get_text(user_id, "admin_full_stop", mapping))
            return
        try:
            bot.copy_message(message.chat.id, STORAGE_CHANNEL_ID, data.get("msg_id"))
            time.sleep(0.3)
        except Exception as e:
            bot.send_message(message.chat.id, get_text(user_id, "full_tag_error", mapping).format(tag=tag, error=e))
            
    if active_processes.get(ADMIN_ID, True):
        bot.send_message(message.chat.id, get_text(user_id, "admin_full_done", mapping))

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = call.from_user
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    mapping = load_mapping()

    if user.id != ADMIN_ID:
        if is_banned(user.id, mapping):
            bot.answer_callback_query(call.id, get_text(user.id, "banned_msg", mapping), show_alert=True)
            return
        if flood_status(user.id):
            bot.answer_callback_query(call.id, get_text(user.id, "flood_warn", mapping))
            return

    if call.data.startswith("setlang_"):
        lang_code = call.data.replace("setlang_", "")
        if "_users_lang" not in mapping:
            mapping["_users_lang"] = {}
        mapping["_users_lang"][str(user.id)] = lang_code
        save_mapping_data(mapping)
        
        is_admin = (user.id == ADMIN_ID)
        set_user_commands(user.id, is_admin, mapping)

        bot.answer_callback_query(call.id, get_text(user.id, "lang_set", mapping))
        
        caption_text = format_welcome_text(user, mapping)
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption_text, reply_markup=get_start_keyboard(user.id, mapping))
        except:
            try:
                bot.edit_message_text(text=caption_text, chat_id=chat_id, message_id=message_id, reply_markup=get_start_keyboard(user.id, mapping))
            except:
                bot.send_message(chat_id, caption_text, reply_markup=get_start_keyboard(user.id, mapping))
        return

    elif call.data == "change_lang":
        bot.send_message(chat_id, get_text(user.id, "select_lang", mapping), reply_markup=get_lang_keyboard())
        bot.answer_callback_query(call.id)
        return

    elif call.data == "open_files":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(get_text(user.id, "btn_new", mapping), callback_data="lst_new_1"),
            InlineKeyboardButton(get_text(user.id, "btn_top", mapping), callback_data="lst_top_1"),
            InlineKeyboardButton(get_text(user.id, "btn_rated", mapping), callback_data="lst_rated_1"),
            InlineKeyboardButton(get_text(user.id, "btn_search", mapping), callback_data="files_search"),
        )
        markup.add(InlineKeyboardButton(get_text(user.id, "back", mapping), callback_data="back_to_main"))
        text = get_text(user.id, "files_menu_title", mapping)
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text, reply_markup=markup)
        except:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    elif call.data.startswith("lst_"):
        _, mode, page_s = call.data.split("_", 2)
        if mode not in ("new", "top", "rated"):
            mode = "new"
        page = int(page_s) if page_s.isdigit() else 1
        items = get_sorted_files(mapping, mode)
        per_page = 6
        total_pages = max(1, (len(items) + per_page - 1) // per_page)
        page = min(max(page, 1), total_pages)
        name = get_text(user.id, {"new": "btn_new", "top": "btn_top", "rated": "btn_rated"}[mode], mapping)
        if items:
            text = get_text(user.id, "list_title", mapping).format(name=name, page=page, total=total_pages) + "\n\n" + get_text(user.id, "pick_file", mapping)
        else:
            text = name + "\n\n" + get_text(user.id, "admin_files_empty", mapping)

        bot_username = bot.get_me().username
        markup = InlineKeyboardMarkup(row_width=1)
        for tag, data in items[(page - 1) * per_page: page * per_page]:
            markup.add(file_button(tag, data, bot_username, list_suffix(mode, data)))
        if total_pages > 1:
            nav = []
            if page > 1:
                nav.append(InlineKeyboardButton("⬅️", callback_data=f"lst_{mode}_{page-1}"))
            nav.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
            if page < total_pages:
                nav.append(InlineKeyboardButton("➡️", callback_data=f"lst_{mode}_{page+1}"))
            markup.row(*nav)
        markup.add(InlineKeyboardButton(get_text(user.id, "back", mapping), callback_data="open_files"))
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text, reply_markup=markup)
        except:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    elif call.data == "files_search":
        admin_states[user.id] = {"action": "user_search"}
        bot.send_message(chat_id, get_text(user.id, "search_prompt", mapping))
        bot.answer_callback_query(call.id)
        return

    elif call.data == "toggle_notify":
        off = mapping.setdefault("_notify_off", [])
        uid_s = str(user.id)
        if uid_s in off:
            off.remove(uid_s)
            toast = get_text(user.id, "notify_on_toast", mapping)
        else:
            off.append(uid_s)
            toast = get_text(user.id, "notify_off_toast", mapping)
        save_mapping_data(mapping)
        bot.answer_callback_query(call.id, toast)
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=get_profile_keyboard(user.id, mapping))
        except Exception:
            pass
        return

    elif call.data == "noop":
        bot.answer_callback_query(call.id)
        return

    elif call.data.startswith("getfile_"):
        file_key = call.data[len("getfile_"):]
        not_subbed = check_user_subscriptions(user.id, mapping)
        if not_subbed:
            bot.send_message(chat_id, get_text(user.id, "sub_required", mapping), reply_markup=get_sub_keyboard(not_subbed, file_key, user.id, mapping))
            bot.answer_callback_query(call.id)
            return
        if file_key in mapping and isinstance(mapping[file_key], dict) and not file_key.startswith("_"):
            mapping[file_key]["downloads"] = mapping[file_key].get("downloads", 0) + 1
            user_key = f"dl_user_{user.id}"
            mapping[file_key][user_key] = mapping[file_key].get(user_key, 0) + 1
            check_user_achievements(user.id, mapping)
            save_mapping_data(mapping)
            bot.answer_callback_query(call.id)
            send_file_to_user(chat_id, file_key, user.id, mapping)
        else:
            bot.answer_callback_query(call.id, get_text(user.id, "file_not_found", mapping), show_alert=True)
        return

    elif call.data.startswith("qrcode_"):
        file_key = call.data.replace("qrcode_", "")
        bot_username = bot.get_me().username
        deep_link = f"https://t.me/{bot_username}?start={file_key}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(deep_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        bio = io.BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, "PNG")
        bio.seek(0)
        
        text = get_text(user.id, "qr_code_caption", mapping).format(tag=file_key, link=deep_link)
        bot.send_photo(chat_id, bio, caption=text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    elif call.data == "open_achievements":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
        dl_count, ref_count, rate_count, sug_count, _ = get_user_metrics(user.id, mapping)
        
        user_achs, changed = check_user_achievements(user.id, mapping)
        if changed:
            save_mapping_data(mapping)
            
        ach_texts = []
        for ach_id, cat, req in ACHIEVEMENTS_CONFIG:
            title_name = get_text(user.id, f"title_{ach_id}", mapping)
            desc_name = get_text(user.id, f"desc_{ach_id}", mapping)
            if ach_id in user_achs:
                ach_texts.append(f"✅ <b>{title_name}</b> ({desc_name})")
            else:
                ach_texts.append(f"🔒 <s>{title_name}</s> ({desc_name})")
                
        achs_str = "\n".join(ach_texts)
        cur_title = get_active_title_str(user.id, mapping) or get_text(user.id, "no_title", mapping)
        
        text = get_text(user.id, "ref_menu_title", mapping).format(
            ref_link=ref_link,
            ref_count=ref_count,
            dl_count=dl_count,
            rate_count=rate_count,
            sug_count=sug_count,
            cur_title=cur_title,
            achievements=achs_str
        )
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(get_text(user.id, "btn_select_title", mapping), callback_data="select_title_menu"),
            InlineKeyboardButton(get_text(user.id, "back", mapping), callback_data="open_profile")
        )
        
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text, reply_markup=markup, parse_mode="HTML")
        except:
            try:
                bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    elif call.data == "select_title_menu":
        user_achs, changed = check_user_achievements(user.id, mapping)
        if changed:
            save_mapping_data(mapping)
            
        if not user_achs:
            bot.answer_callback_query(call.id, get_text(user.id, "no_titles_unlocked", mapping), show_alert=True)
            return
            
        markup = InlineKeyboardMarkup(row_width=2)
        btns = []
        for ach_id in user_achs:
            t_name = get_text(user.id, f"title_{ach_id}", mapping)
            btns.append(InlineKeyboardButton(f"🎖 {t_name}", callback_data=f"equip_title_{ach_id}"))
        markup.add(*btns)
        markup.add(
            InlineKeyboardButton(get_text(user.id, "btn_clear_title", mapping), callback_data="equip_title_none"),
            InlineKeyboardButton(get_text(user.id, "back", mapping), callback_data="open_achievements")
        )
        
        prompt_text = get_text(user.id, "select_title_prompt", mapping)
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=prompt_text, reply_markup=markup)
        except:
            bot.edit_message_text(text=prompt_text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    elif call.data.startswith("equip_title_"):
        ach_id = call.data.replace("equip_title_", "")
        uid_str = str(user.id)
        if "_active_title" not in mapping:
            mapping["_active_title"] = {}
            
        if ach_id == "none":
            mapping["_active_title"].pop(uid_str, None)
            save_mapping_data(mapping)
            bot.answer_callback_query(call.id, get_text(user.id, "title_cleared", mapping))
        else:
            user_achs, _ = check_user_achievements(user.id, mapping)
            if ach_id in user_achs:
                mapping["_active_title"][uid_str] = ach_id
                save_mapping_data(mapping)
                t_name = get_text(user.id, f"title_{ach_id}", mapping)
                bot.answer_callback_query(call.id, get_text(user.id, "title_equipped", mapping).format(title=t_name))
                
        call.data = "open_achievements"
        handle_callback_query(call)
        return

    elif call.data == "click_suggest":
        admin_states[user.id] = {"action": "suggest_file"}
        bot.send_message(chat_id, get_text(user.id, "suggest_prompt", mapping))
        bot.answer_callback_query(call.id)

    elif call.data == "click_commands":
        is_admin = (user.id == ADMIN_ID)
        if is_admin:
            text = (
                f"{get_text(user.id, 'help_admin_title', mapping)}\n\n"
                f"/start — {get_text(user.id, 'cmd_start', mapping)}\n"
                f"/add — {get_text(user.id, 'cmd_add', mapping)}\n"
                f"/edit [{get_text(user.id, 'arg_tag', mapping)}] — {get_text(user.id, 'cmd_edit', mapping)}\n"
                f"/del [{get_text(user.id, 'arg_tag', mapping)}] — {get_text(user.id, 'cmd_del', mapping)}\n"
                f"/stats — {get_text(user.id, 'cmd_stats', mapping)}\n"
                f"/ban [{get_text(user.id, 'arg_id', mapping)}] — {get_text(user.id, 'cmd_ban', mapping)}\n"
                f"/unban [{get_text(user.id, 'arg_id', mapping)}] — {get_text(user.id, 'cmd_unban', mapping)}\n"
                f"/broadcast [{get_text(user.id, 'arg_text', mapping)}] — {get_text(user.id, 'cmd_broadcast', mapping)}\n"
                f"/files — {get_text(user.id, 'cmd_files', mapping)}\n"
                f"/search [{get_text(user.id, 'arg_query', mapping)}] — {get_text(user.id, 'cmd_search', mapping)}\n"
                f"/full — {get_text(user.id, 'cmd_full', mapping)}\n"
                f"/stop — {get_text(user.id, 'cmd_stop', mapping)}\n"
                f"/db — {get_text(user.id, 'cmd_db', mapping)}\n"
                f"/update_db — {get_text(user.id, 'cmd_update_db', mapping)}\n"
                f"/stats_files — {get_text(user.id, 'cmd_stats_files', mapping)}\n"
                f"/links — {get_text(user.id, 'cmd_links', mapping)}\n"
                f"/suggest — {get_text(user.id, 'cmd_suggest', mapping)}\n"
                f"/check_vt — {get_text(user.id, 'cmd_check_vt', mapping)}\n"
                f"/help — {get_text(user.id, 'cmd_help', mapping)}"
            )
        else:
            text = (
                f"{get_text(user.id, 'help_user_title', mapping)}\n\n"
                f"/start — {get_text(user.id, 'cmd_start', mapping)}\n"
                f"/search [{get_text(user.id, 'arg_query', mapping)}] — {get_text(user.id, 'cmd_search', mapping)}\n"
                f"/suggest — {get_text(user.id, 'cmd_suggest', mapping)}\n"
                f"/check_vt — {get_text(user.id, 'cmd_check_vt', mapping)}\n"
                f"/help — {get_text(user.id, 'cmd_help', mapping)}"
            )
        bot.send_message(chat_id, text)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("fav_toggle_"):
        file_key = call.data.replace("fav_toggle_", "")
        if "_favorites" not in mapping:
            mapping["_favorites"] = {}
        user_favs = mapping["_favorites"].get(str(user.id), [])
        
        if file_key in user_favs:
            user_favs.remove(file_key)
            bot.answer_callback_query(call.id, get_text(user.id, "fav_removed", mapping))
        else:
            user_favs.append(file_key)
            bot.answer_callback_query(call.id, get_text(user.id, "fav_added", mapping))
            
        mapping["_favorites"][str(user.id)] = user_favs
        save_mapping_data(mapping)
        
        is_fav = file_key in user_favs
        fav_btn_text = get_text(user.id, "btn_fav_del" if is_fav else "btn_fav_add", mapping)
        
        markup = InlineKeyboardMarkup(row_width=5)
        markup.add(
            InlineKeyboardButton("⭐ 1", callback_data=f"rate_{file_key}_1"),
            InlineKeyboardButton("⭐ 2", callback_data=f"rate_{file_key}_2"),
            InlineKeyboardButton("⭐ 3", callback_data=f"rate_{file_key}_3"),
            InlineKeyboardButton("⭐ 4", callback_data=f"rate_{file_key}_4"),
            InlineKeyboardButton("⭐ 5", callback_data=f"rate_{file_key}_5")
        )
        report_btn_text = get_text(user.id, "report_btn", mapping)
        markup.add(
            InlineKeyboardButton(fav_btn_text, callback_data=f"fav_toggle_{file_key}"),
            InlineKeyboardButton(report_btn_text, callback_data=f"report_menu_{file_key}")
        )
        markup.add(
            InlineKeyboardButton(get_text(user.id, "btn_qr_code", mapping), callback_data=f"qrcode_{file_key}")
        )
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
        except Exception:
            pass
        return

    elif call.data.startswith("open_favorites_"):
        page = int(call.data.replace("open_favorites_", ""))
        if "_favorites" not in mapping:
            mapping["_favorites"] = {}
        user_favs = mapping["_favorites"].get(str(user.id), [])
        
        if not user_favs:
            bot.answer_callback_query(call.id, get_text(user.id, "favorites_empty", mapping), show_alert=True)
            return
            
        items_per_page = 3
        total_items = len(user_favs)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        if page < 1: page = 1
        if page > total_pages: page = total_pages
        
        start_idx = (page - 1) * items_per_page
        current_keys = user_favs[start_idx:start_idx + items_per_page]
        
        bot_username = bot.get_me().username
        text = f"{get_text(user.id, 'favorites_title', mapping)} {get_text(user.id, 'page_suffix', mapping).format(page=page, total=total_pages)}\n\n"
        for tag in current_keys:
            if tag in mapping:
                link = f"https://t.me/{bot_username}?start={tag}"
                desc = mapping[tag].get("desc", "")
                text += f"🔗 {link}\n"
                if desc:
                    text += f"📝 {desc}\n"
                text += "\n"
                
        markup = InlineKeyboardMarkup(row_width=3)
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"open_favorites_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"open_favorites_{page+1}"))
        if nav_buttons:
            markup.add(*nav_buttons)
        markup.add(InlineKeyboardButton(get_text(user.id, "back", mapping), callback_data="open_profile"))
        
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            try:
                bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
            except:
                bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    elif call.data.startswith("rate_"):
        parts = call.data.split("_")
        file_key = parts[1]
        stars = parts[2]
        thanks_msg = get_text(user.id, "rate_thanks", mapping)
        bot.answer_callback_query(call.id, f"{thanks_msg}{stars}/5!")
        
        if file_key in mapping:
            if "ratings" not in mapping[file_key]:
                mapping[file_key]["ratings"] = []
            mapping[file_key]["ratings"] = [r for r in mapping[file_key]["ratings"] if r.get("user_id") != user.id]
            mapping[file_key]["ratings"].append({"user_id": user.id, "stars": int(stars)})
            check_user_achievements(user.id, mapping)
            save_mapping_data(mapping)
        return

    elif call.data.startswith("report_menu_"):
        file_key = call.data.replace("report_menu_", "")
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(get_text(user.id, "reason_virus", mapping), callback_data=f"report_send_{file_key}_virus"),
            InlineKeyboardButton(get_text(user.id, "reason_outdated", mapping), callback_data=f"report_send_{file_key}_outdated"),
            InlineKeyboardButton(get_text(user.id, "reason_broken", mapping), callback_data=f"report_send_{file_key}_broken"),
            InlineKeyboardButton(get_text(user.id, "reason_other", mapping), callback_data=f"report_send_{file_key}_other"),
            InlineKeyboardButton(get_text(user.id, "back", mapping), callback_data=f"back_to_rates_{file_key}")
        )
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    elif call.data.startswith("back_to_rates_"):
        file_key = call.data.replace("back_to_rates_", "")
        user_favs = mapping.get("_favorites", {}).get(str(user.id), [])
        is_fav = file_key in user_favs
        fav_btn_text = get_text(user.id, "btn_fav_del" if is_fav else "btn_fav_add", mapping)

        markup = InlineKeyboardMarkup(row_width=5)
        markup.add(
            InlineKeyboardButton("⭐ 1", callback_data=f"rate_{file_key}_1"),
            InlineKeyboardButton("⭐ 2", callback_data=f"rate_{file_key}_2"),
            InlineKeyboardButton("⭐ 3", callback_data=f"rate_{file_key}_3"),
            InlineKeyboardButton("⭐ 4", callback_data=f"rate_{file_key}_4"),
            InlineKeyboardButton("⭐ 5", callback_data=f"rate_{file_key}_5")
        )
        markup.add(
            InlineKeyboardButton(fav_btn_text, callback_data=f"fav_toggle_{file_key}"),
            InlineKeyboardButton(get_text(user.id, "report_btn", mapping), callback_data=f"report_menu_{file_key}")
        )
        markup.add(
            InlineKeyboardButton(get_text(user.id, "btn_qr_code", mapping), callback_data=f"qrcode_{file_key}")
        )
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    elif call.data.startswith("report_send_"):
        parts = call.data.split("_")
        file_key = parts[2]
        reason_type = parts[3]
        
        reason_desc = get_text(user.id, f"reason_{reason_type}", mapping)
        t_title = get_text(user.id, "report_title", mapping)
        t_tag = get_text(user.id, "report_tag", mapping)
        t_reason = get_text(user.id, "report_reason", mapping)
        t_user = get_text(user.id, "report_user", mapping)

        report_text = (
            f"{t_title}\n\n"
            f"{t_tag}: `{file_key}`\n"
            f"{t_reason}: {reason_desc}\n"
            f"{t_user}: [{user.first_name}](tg://user?id={user.id}) (ID: `{user.id}`)"
        )
        bot.send_message(ADMIN_ID, report_text, parse_mode="Markdown")
        bot.answer_callback_query(call.id, get_text(user.id, "report_success", mapping), show_alert=True)
        return

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
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0, "desc": user_description, "category": "General"}
            
            if "_approved_suggests" not in mapping:
                mapping["_approved_suggests"] = {}
            t_uid_str = str(target_user_id)
            mapping["_approved_suggests"][t_uid_str] = mapping["_approved_suggests"].get(t_uid_str, 0) + 1
            check_user_achievements(target_user_id, mapping)
            
            save_mapping_data(mapping)

            if call.message.caption:
                bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f"{caption}\n\n{get_text(user.id, 'status_approved', mapping)}", parse_mode="Markdown")
            else:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=get_text(user.id, "status_approved", mapping))
            bot.send_message(target_user_id, get_text(target_user_id, "suggest_approved_user", mapping))
        except Exception as e:
            bot.send_message(chat_id, get_text(user.id, "error_generic", mapping).format(error=e))
        bot.answer_callback_query(call.id, get_text(user.id, "toast_approved", mapping))

    elif call.data.startswith("reject_suggest_"):
        parts = call.data.split("_")
        target_user_id = int(parts[2])
        try:
            if call.message.caption:
                bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f"{call.message.caption}\n\n{get_text(user.id, 'status_rejected', mapping)}", parse_mode="Markdown")
            else:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=get_text(user.id, "status_rejected", mapping))
            bot.send_message(target_user_id, get_text(target_user_id, "suggest_rejected_user", mapping))
        except Exception as e:
            print(f"Error rejecting: {e}")
        bot.answer_callback_query(call.id, get_text(user.id, "toast_rejected", mapping))

    elif call.data.startswith("edit_approve_suggest_"):
        parts = call.data.split("_")
        target_user_id = int(parts[3])
        admin_states[ADMIN_ID] = {
            "action": "edit_approve_save",
            "target_user_id": target_user_id,
            "message_id": message_id,
            "original_message": call.message
        }
        bot.send_message(ADMIN_ID, get_text(user.id, "edit_approve_prompt", mapping))
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
        bot.send_message(ADMIN_ID, get_text(user.id, "reject_reason_prompt", mapping))
        bot.answer_callback_query(call.id)

    elif call.data.startswith("files_page_"):
        parts = call.data.split("_")
        page = int(parts[2])
        query = "_".join(parts[3:]) if len(parts) > 3 else ""
        show_files_page(chat_id, message_id, page=page, search_query=query, user_id=user.id)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("sub_check_"):
        file_key = call.data.replace("sub_check_", "")
        mapping = load_mapping()
        not_subbed = check_user_subscriptions(user.id, mapping)
        
        if not_subbed:
            bot.answer_callback_query(call.id, get_text(user.id, "sub_fail", mapping), show_alert=True)
        else:
            bot.answer_callback_query(call.id, get_text(user.id, "sub_success", mapping))
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
                
                check_user_achievements(user.id, mapping)
                save_mapping_data(mapping)
                send_file_to_user(chat_id, file_key, user.id, mapping)
            else:
                bot.send_message(chat_id, get_text(user.id, "file_not_found", mapping))

    elif call.data == "open_profile":
        first_name = user.first_name
        user_id = user.id
        username = f"@{user.username}" if user.username else "—"
        
        uptime_seconds = int(time.time() - START_TIME)
        if uptime_seconds < 0:
            uptime_seconds = 0
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        mapping = load_mapping()
        uptime_str = get_text(user_id, "uptime_fmt", mapping).format(d=days, h=hours, m=minutes, s=seconds)
        user_key = f"dl_user_{user_id}"
        my_downloads = sum(item.get(user_key, 0) for key, item in mapping.items() if not key.startswith("_") and isinstance(item, dict))
        total_downloads = sum(item.get("downloads", 0) for key, item in mapping.items() if not key.startswith("_") and isinstance(item, dict))
        fav_count = len(mapping.get("_favorites", {}).get(str(user_id), []))
        cur_title = get_active_title_str(user_id, mapping) or get_text(user_id, "no_title", mapping)

        t_title = get_text(user_id, "profile_title", mapping)
        t_id = get_text(user_id, "profile_id", mapping)
        t_name = get_text(user_id, "profile_name", mapping)
        t_tline = get_text(user_id, "profile_title_line", mapping)
        t_uname = get_text(user_id, "profile_username", mapping)
        t_uptime = get_text(user_id, "profile_uptime", mapping)
        t_mydl = get_text(user_id, "profile_my_dl", mapping)
        t_totaldl = get_text(user_id, "profile_total_dl", mapping)
        t_favcount = get_text(user_id, "profile_fav_count", mapping)

        profile_caption = (
            f"{t_title}\n\n"
            f"{t_id}: {user_id}\n"
            f"{t_name}: {first_name}\n"
            f"{t_tline}: {cur_title}\n"
            f"{t_uname}: {username}\n"
            f"{t_uptime}: {uptime_str}\n"
            f"{t_mydl}: {my_downloads}\n"
            f"{t_totaldl}: {total_downloads}\n"
            f"{t_favcount}: {fav_count}"
        )
        
        try:
            with open("2.jpg", "rb") as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo.read(), caption=profile_caption),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard(user.id, mapping)
                )
        except Exception:
            try:
                bot.edit_message_caption(
                    caption=profile_caption,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard(user.id, mapping)
                )
            except Exception:
                bot.edit_message_text(
                    text=profile_caption,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_profile_keyboard(user.id, mapping)
                )
        bot.answer_callback_query(call.id)

    elif call.data == "back_to_main":
        caption_text = format_welcome_text(user, mapping)
        try:
            with open("1.png", "rb") as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo.read(), caption=caption_text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard(user.id, mapping)
                )
        except Exception:
            try:
                bot.edit_message_caption(
                    caption=caption_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard(user.id, mapping)
                )
            except Exception:
                bot.edit_message_text(
                    text=caption_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_start_keyboard(user.id, mapping)
                )
        bot.answer_callback_query(call.id)

def send_file_to_user(chat_id, file_key, user_id=None, mapping=None):
    if mapping is None:
        mapping = load_mapping()
    if user_id is None:
        user_id = ADMIN_ID

    if file_key in mapping:
        item = mapping[file_key]
        try:
            user_favs = mapping.get("_favorites", {}).get(str(user_id), [])
            is_fav = file_key in user_favs
            fav_btn_text = get_text(user_id, "btn_fav_del" if is_fav else "btn_fav_add", mapping)

            markup = InlineKeyboardMarkup(row_width=5)
            markup.add(
                InlineKeyboardButton("⭐ 1", callback_data=f"rate_{file_key}_1"),
                InlineKeyboardButton("⭐ 2", callback_data=f"rate_{file_key}_2"),
                InlineKeyboardButton("⭐ 3", callback_data=f"rate_{file_key}_3"),
                InlineKeyboardButton("⭐ 4", callback_data=f"rate_{file_key}_4"),
                InlineKeyboardButton("⭐ 5", callback_data=f"rate_{file_key}_5")
            )
            report_btn_text = get_text(user_id, "report_btn", mapping)
            markup.add(
                InlineKeyboardButton(fav_btn_text, callback_data=f"fav_toggle_{file_key}"),
                InlineKeyboardButton(report_btn_text, callback_data=f"report_menu_{file_key}")
            )
            markup.add(
                InlineKeyboardButton(get_text(user_id, "btn_qr_code", mapping), callback_data=f"qrcode_{file_key}")
            )

            bot.copy_message(chat_id, STORAGE_CHANNEL_ID, item['msg_id'])
            avg, n_r = get_avg_rating(item)
            info_line = (get_text(user_id, "rating_line", mapping).format(avg=f"{avg:.1f}", n=n_r, dl=item.get("downloads", 0)) if n_r
                         else get_text(user_id, "file_downloads_line", mapping).format(count=item.get("downloads", 0)))
            rate_prompt_text = get_text(user_id, "rate_prompt", mapping) + "\n\n" + info_line
            bot.send_message(chat_id, rate_prompt_text, reply_markup=markup)
            
            _, changed = check_user_achievements(user_id, mapping)
            if changed:
                save_mapping_data(mapping)
            return
        except Exception as e:
            print(f"Помилка відправки файлу: {e}")
    bot.send_message(chat_id, get_text(user_id, "file_not_found", mapping))

def notify_users(text_key, mapping, **fmt):
    users_lang = mapping.get("_users_lang", {})
    for uid_str in users_lang.keys():
        if uid_str in mapping.get("_notify_off", []) or uid_str in mapping.get("_banned", []):
            continue
        try:
            bot.send_message(int(uid_str), get_text(int(uid_str), text_key, mapping).format(**fmt))
            time.sleep(0.05)
        except Exception:
            pass

@bot.message_handler(commands=["add"])
def add_file_step1(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    admin_states[ADMIN_ID] = {"action": "add"}
    bot.send_message(message.chat.id, get_text(user_id, "admin_add_prompt", mapping))

@bot.message_handler(commands=["edit"])
def edit_file_step1(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, get_text(user_id, "admin_edit_usage", mapping))
        return
    tag = args[1].strip()
    if tag not in mapping:
        bot.send_message(message.chat.id, get_text(user_id, "admin_edit_not_found", mapping))
        return
    admin_states[ADMIN_ID] = {"action": "edit", "tag": tag}
    bot.send_message(message.chat.id, f"{get_text(user_id, 'admin_edit_prompt', mapping)} `{tag}`:")

@bot.message_handler(commands=["del"])
def delete_file(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "⚠️ Укажите тег для удаления: `/del tag`", parse_mode="Markdown")
        return
    tag = args[1].strip()
    if tag in mapping:
        try:
            bot.delete_message(STORAGE_CHANNEL_ID, mapping[tag]['msg_id'])
        except Exception as e:
            print(f"Не удалось удалить сообщение из канала: {e}")
        del mapping[tag]
        save_mapping_data(mapping)
        bot.send_message(message.chat.id, get_text(user_id, "file_deleted", mapping).format(tag=tag))
    else:
        bot.send_message(message.chat.id, get_text(user_id, "admin_edit_not_found", mapping))

@bot.message_handler(commands=["stats"])
def stats_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    files = {k: v for k, v in mapping.items() if not k.startswith("_") and isinstance(v, dict)}
    total_dl = sum(v.get("downloads", 0) for v in files.values())
    top = sorted(files.items(), key=lambda x: x[1].get("downloads", 0), reverse=True)[:5]
    top_text = "\n".join(f"{i}. {t} — {d.get('downloads', 0)} 📥" for i, (t, d) in enumerate(top, 1)) or "—"
    text = get_text(user_id, "stats_overview", mapping).format(
        users=len(mapping.get("_users_lang", {})), banned=len(mapping.get("_banned", [])),
        files=len(files), downloads=total_dl, top=top_text)
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["ban", "unban"])
def ban_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    args = message.text.split()
    cmd = args[0].lstrip("/").split("@")[0].lower()
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(message.chat.id, get_text(user_id, "ban_usage", mapping))
        return
    target = args[1]
    banned = mapping.setdefault("_banned", [])
    if cmd == "ban":
        if int(target) == ADMIN_ID:
            bot.send_message(message.chat.id, get_text(user_id, "ban_admin", mapping))
            return
        if target not in banned:
            banned.append(target)
        save_mapping_data(mapping)
        bot.send_message(message.chat.id, get_text(user_id, "ban_done", mapping).format(uid=target))
    else:
        if target in banned:
            banned.remove(target)
        save_mapping_data(mapping)
        bot.send_message(message.chat.id, get_text(user_id, "unban_done", mapping).format(uid=target))

@bot.message_handler(commands=["broadcast"])
def broadcast_cmd(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.send_message(message.chat.id, get_text(user_id, "broadcast_usage", mapping))
        return
    text = parts[1].strip()
    banned = mapping.get("_banned", [])
    targets = [int(u) for u in mapping.get("_users_lang", {}) if u not in banned]
    bot.send_message(message.chat.id, get_text(user_id, "broadcast_started", mapping))

    def worker():
        ok = fail = 0
        for uid in targets:
            try:
                bot.send_message(uid, text)
                ok += 1
            except Exception:
                fail += 1
            time.sleep(0.05)
        bot.send_message(message.chat.id, get_text(user_id, "broadcast_done", mapping).format(ok=ok, fail=fail))

    Thread(target=worker, daemon=True).start()

@bot.message_handler(commands=["links"])
def manage_links(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "admin_no_rights", mapping))
        return
    
    args = message.text.split(maxsplit=2)
    settings = get_settings(mapping)
    channels = settings.get("channels", ["@goat1488_67"])

    if len(args) < 2:
        header = get_text(user_id, "links_header", mapping)
        text = header + "\n".join(channels) + "\n\n" + get_text(user_id, "links_usage", mapping)
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        return

    action = args[1].lower()
    if len(args) < 3:
        bot.send_message(message.chat.id, get_text(user_id, "links_usage", mapping))
        return
        
    ch_target = args[2].strip()
    if not ch_target.startswith("@"):
        ch_target = "@" + ch_target

    if action == "add":
        if ch_target not in channels:
            channels.append(ch_target)
            settings["channels"] = channels
            save_mapping_data(mapping)
            msg_added = get_text(user_id, "links_added", mapping)
            bot.send_message(message.chat.id, f"{msg_added} {ch_target}")
        else:
            bot.send_message(message.chat.id, get_text(user_id, "link_exists", mapping).format(channel=ch_target))
    elif action == "del":
        if ch_target in channels and len(channels) > 1:
            channels.remove(ch_target)
            settings["channels"] = channels
            save_mapping_data(mapping)
            msg_del = get_text(user_id, "links_deleted", mapping)
            bot.send_message(message.chat.id, f"{msg_del} {ch_target}")
        else:
            bot.send_message(message.chat.id, get_text(user_id, "link_cannot_delete", mapping))

@bot.message_handler(content_types=["document", "photo", "video", "text"])
def handle_incoming_file(message):
    user_id = message.from_user.id
    mapping = load_mapping()
    
    if message.document and message.document.file_name and message.document.file_name.endswith(".zip") and user_id == ADMIN_ID:
        bot.send_message(message.chat.id, get_text(user_id, "zip_upload_start", mapping))
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            zip_bio = io.BytesIO(downloaded_file)
            imported_count = 0
            
            with zipfile.ZipFile(zip_bio, 'r') as zf:
                for filename in zf.namelist():
                    if filename.endswith('/') or filename.startswith('__MACOSX'):
                        continue
                    file_data = zf.read(filename)
                    tag = os.path.splitext(os.path.basename(filename))[0]
                    
                    sent_msg = bot.send_document(
                        STORAGE_CHANNEL_ID, 
                        io.BytesIO(file_data), 
                        visible_file_name=filename, 
                        caption=f"#{tag}\n\nІмпортовано з ZIP-архіву"
                    )
                    
                    mapping[tag] = {
                        "msg_id": sent_msg.message_id,
                        "downloads": 0,
                        "desc": f"Архівний файл: {filename}",
                        "category": "Archive"
                    }
                    imported_count += 1
                    
            save_mapping_data(mapping)
            bot.send_message(message.chat.id, get_text(user_id, "zip_upload_done", mapping).format(count=imported_count))
        except Exception as e:
            bot.send_message(message.chat.id, get_text(user_id, "zip_error", mapping).format(error=e))
        return

    state = admin_states.get(user_id, {})
    action = state.get("action")
    
    if not action:
        return

    text = message.caption or message.text or ""
    if user_id != ADMIN_ID and guard_message(message, mapping):
        admin_states.pop(user_id, None)
        return

    if action == "edit_approve_save":
        target_user_id = state.get("target_user_id")
        orig_msg = state.get("original_message")
        msg_id_to_edit = state.get("message_id")

        parts = text.split(maxsplit=1)
        if not parts:
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
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0, "desc": user_description, "category": "General"}
            
            if "_approved_suggests" not in mapping:
                mapping["_approved_suggests"] = {}
            t_uid_str = str(target_user_id)
            mapping["_approved_suggests"][t_uid_str] = mapping["_approved_suggests"].get(t_uid_str, 0) + 1
            check_user_achievements(target_user_id, mapping)
            
            save_mapping_data(mapping)

            if orig_msg.caption:
                bot.edit_message_caption(chat_id=ADMIN_ID, message_id=msg_id_to_edit, caption=f"{orig_msg.caption}\n\n{get_text(ADMIN_ID, 'status_approved_edited', mapping)}", parse_mode="Markdown")
            else:
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=msg_id_to_edit, text=get_text(ADMIN_ID, "status_approved_edited", mapping))
            bot.send_message(target_user_id, get_text(target_user_id, "suggest_approved_link_user", mapping).format(link=deep_link))
            
            notify_users("notify_new_available", mapping, link=deep_link, desc=user_description)
        except Exception as e:
            bot.send_message(ADMIN_ID, get_text(ADMIN_ID, "error_generic", mapping).format(error=e))

        admin_states.pop(user_id, None)
        return

    elif action == "edit_reject_save":
        target_user_id = state.get("target_user_id")
        orig_msg = state.get("original_message")
        msg_id_to_edit = state.get("message_id")
        reason = text.strip()

        try:
            if orig_msg.caption:
                bot.edit_message_caption(chat_id=ADMIN_ID, message_id=msg_id_to_edit, caption=f"{orig_msg.caption}\n\n{get_text(ADMIN_ID, 'status_rejected_reason', mapping).format(reason=reason)}", parse_mode="Markdown")
            else:
                bot.edit_message_text(chat_id=ADMIN_ID, message_id=msg_id_to_edit, text=get_text(ADMIN_ID, "status_rejected_reason", mapping).format(reason=reason))
            bot.send_message(target_user_id, get_text(target_user_id, "suggest_rejected_reason_user", mapping).format(reason=reason))
        except Exception as e:
            bot.send_message(ADMIN_ID, get_text(ADMIN_ID, "error_generic", mapping).format(error=e))

        admin_states.pop(user_id, None)
        return

    elif action == "suggest_file":
        parts = text.split(maxsplit=1)
        if not parts:
            bot.send_message(message.chat.id, get_text(user_id, "suggest_need_tag", mapping))
            admin_states.pop(user_id, None)
            return

        tag = parts[0].strip()
        user_description = parts[1] if len(parts) > 1 else ""
        user_name = message.from_user.first_name
        
        forward_caption = f"#{tag}\n\n{user_description}\n\n{get_text(ADMIN_ID, 'suggested_by', mapping)} [{user_name}](tg://user?id={user_id})"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(get_text(ADMIN_ID, "btn_approve", mapping), callback_data=f"approve_suggest_{user_id}"),
            InlineKeyboardButton(get_text(ADMIN_ID, "btn_reject", mapping), callback_data=f"reject_suggest_{user_id}"),
            InlineKeyboardButton(get_text(ADMIN_ID, "btn_edit_approve", mapping), callback_data=f"edit_approve_suggest_{user_id}"),
            InlineKeyboardButton(get_text(ADMIN_ID, "btn_edit_reject", mapping), callback_data=f"edit_reject_suggest_{user_id}")
        )

        try:
            if message.content_type == "photo":
                bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=forward_caption, reply_markup=markup, parse_mode="Markdown")
            elif message.content_type == "document":
                bot.send_document(ADMIN_ID, message.document.file_id, caption=forward_caption, reply_markup=markup, parse_mode="Markdown")
            elif message.content_type == "video":
                bot.send_video(ADMIN_ID, message.video.file_id, caption=forward_caption, reply_markup=markup, parse_mode="Markdown")
            else:
                bot.copy_message(ADMIN_ID, message.chat.id, message.message_id, caption=forward_caption, reply_markup=markup, parse_mode="Markdown")

            bot.send_message(message.chat.id, get_text(user_id, "suggest_success", mapping))
        except Exception as e:
            bot.send_message(message.chat.id, get_text(user_id, "error_generic", mapping).format(error=e))

        admin_states.pop(user_id, None)
        return

    elif action == "user_search":
        admin_states.pop(user_id, None)
        query = text.strip()
        if query and not query.startswith("/"):
            send_search_results(message.chat.id, user_id, query, mapping)
        return

    elif action == "check_vt_file":
        if not VT_API_KEY:
            bot.send_message(message.chat.id, get_text(user_id, "vt_no_key", mapping))
            admin_states.pop(user_id, None)
            return
            
        if message.content_type == "text" and (text.startswith("http://") or text.startswith("https://")):
            bot.send_message(message.chat.id, get_text(user_id, "vt_checking_url", mapping))
            try:
                headers = {'x-apikey': VT_API_KEY}
                url_bytes = text.encode("utf-8")
                url_id = base64.urlsafe_b64encode(url_bytes).decode("utf-8").strip("=")
                requests.post('https://www.virustotal.com/api/v3/urls', data={'url': text}, headers=headers, timeout=15)
                report_url = f"https://www.virustotal.com/gui/url/{url_id}"
                bot.send_message(message.chat.id, f"{get_text(user_id, 'vt_success_url', mapping)} {report_url}")
            except Exception as e:
                bot.send_message(message.chat.id, get_text(user_id, "error_generic", mapping).format(error=e))
            admin_states.pop(user_id, None)
            return

        if message.document or message.photo:
            bot.send_message(message.chat.id, get_text(user_id, "vt_checking_file", mapping))
            try:
                file_info = bot.get_file(message.document.file_id if message.document else message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                
                files = {'file': (message.document.file_name if message.document else "file.bin", downloaded_file)}
                headers = {'x-apikey': VT_API_KEY}
                
                response = requests.post('https://www.virustotal.com/api/v3/files', files=files, headers=headers, timeout=15)
                file_hash = hashlib.sha256(downloaded_file).hexdigest()
                report_url = f"https://www.virustotal.com/gui/file/{file_hash}"
                
                if response.status_code == 200:
                    bot.send_message(message.chat.id, f"{get_text(user_id, 'vt_success_file', mapping)} {report_url}")
                else:
                    err_data = response.json()
                    err_code = err_data.get("error", {}).get("code", "")
                    if err_code == "AlreadySubmittedError":
                        bot.send_message(message.chat.id, f"{get_text(user_id, 'vt_already', mapping)} {report_url}")
                    else:
                        bot.send_message(message.chat.id, get_text(user_id, "vt_error", mapping).format(error=response.text))
            except Exception as e:
                bot.send_message(message.chat.id, get_text(user_id, "error_generic", mapping).format(error=e))
        else:
            bot.send_message(message.chat.id, get_text(user_id, "vt_send_file_or_link", mapping))
            
        admin_states.pop(user_id, None)
        return

    if user_id != ADMIN_ID:
        return

    parts = text.split(maxsplit=1)

    if action == "add":
        if not parts:
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
            mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": 0, "desc": user_description, "category": "General"}
            save_mapping_data(mapping)
            bot.send_message(message.chat.id, f"{get_text(user_id, 'admin_saved', mapping)} {tag} - {deep_link}")
            
            notify_users("notify_new_added", mapping, link=deep_link, desc=user_description)
        except Exception as e:
            bot.send_message(message.chat.id, get_text(user_id, "error_generic", mapping).format(error=e))

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
            existing_category = mapping[tag].get("category", "General")
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

                mapping[tag] = {"msg_id": sent_msg.message_id, "downloads": downloads_count, "desc": user_description, "category": existing_category}
                save_mapping_data(mapping)
                bot.send_message(message.chat.id, get_text(user_id, "admin_updated", mapping))
                
                notify_users("notify_updated", mapping, link=deep_link, desc=user_description)
            except Exception as e:
                bot.send_message(message.chat.id, get_text(user_id, "error_generic", mapping).format(error=e))

    admin_states.pop(user_id, None)

def daily_stats_scheduler():
    while True:
        now = datetime.now()
        target_time = dtime(21, 0)
        current_time = now.time()
        
        target_seconds = target_time.hour * 3600 + target_time.minute * 60
        current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
        
        sleep_seconds = target_seconds - current_seconds
        if sleep_seconds < 0:
            sleep_seconds += 86400
            
        time.sleep(sleep_seconds)
        
        try:
            mapping = load_mapping()
            total_downloads = sum(item.get("downloads", 0) for key, item in mapping.items() if not key.startswith("_") and isinstance(item, dict))
            files_count = len([k for k in mapping.keys() if not k.startswith("_")])
            
            trend_bar = "📈 Тренд активності: █ ▇ ▆ ▄ ▂ (Стабільно високий)"
            stats_text = (
                f"{get_text(ADMIN_ID, 'daily_stats_title', mapping)}\n"
                f"{get_text(ADMIN_ID, 'daily_stats_date', mapping).format(date=datetime.now().strftime('%Y-%m-%d'))}\n\n"
                f"{get_text(ADMIN_ID, 'daily_stats_files', mapping).format(count=files_count)}\n"
                f"{get_text(ADMIN_ID, 'daily_stats_downloads', mapping).format(count=total_downloads)}\n\n"
                f"{trend_bar}"
            )
            bot.send_message(ADMIN_ID, stats_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Stats error: {e}")
        
        time.sleep(60)

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
    
    stats_thread = Thread(target=daily_stats_scheduler, daemon=True)
    stats_thread.start()
    
    bot.infinity_polling()

