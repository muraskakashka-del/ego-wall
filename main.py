import time
import os
import random
import threading
import sqlite3
from telebot import TeleBot
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8800501422:AAE7OgfZVykpJIUwEYVh4nqESzObDOe2iEU"
GROUP_CHAT_ID = -1004358584206
MY_USERNAME = "Zanyal0x"  # Твой точный юзернейм с НУЛЕМ

bot = TeleBot(BOT_TOKEN)
bot.remove_webhook()

# --- РАБОТА С БАЗОЙ ДАННЫХ (SQLite) ---
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            text TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER,
            username TEXT,
            PRIMARY KEY (chat_id, username)
        )
    ''')
    conn.commit()
    conn.close()

def save_message(chat_id, text):
    if not text:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (chat_id, text) VALUES (?, ?)", (chat_id, text))
    conn.commit()
    conn.close()

def get_random_message(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM messages WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None

def save_user(chat_id, username):
    if not username:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)", (chat_id, username.lower().strip()))
    conn.commit()
    conn.close()

# Инициализируем БД при старте
init_db()

# --- ВЕБ-СЕРВЕР ДЛЯ СВЯЗИ С РЕНДЕРОМ ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive :)")

def run_web_server():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, WebServerHandler)
    print("Веб-сервер запущен на порту 8080...")
    httpd.serve_forever()

# --- АВТОМАТИЧЕСКИЙ СПАМ КАЖДЫЙ ЧАС ---
def spammer():
    while True:
        try:
            delay = random.randint(1, 3600)
            print(f"[Спамер] Ожидание перед отправкой: {delay} сек.")
            time.sleep(delay)
            
            text_to_send = get_random_message(GROUP_CHAT_ID)
            if text_to_send:
                bot.send_message(GROUP_CHAT_ID, text_to_send)
                print(f"[Спамер] Отправлено: {text_to_send}")
            else:
                bot.send_message(GROUP_CHAT_ID, "Я за вами слежу 👁")
            
            remaining_time = 3600 - delay
            if remaining_time > 0:
                time.sleep(remaining_time)
                
        except Exception as e:
            print(f"Ошибка спамера: {e}")
            time.sleep(10)

# --- ОБРАБОТКА СООБЩЕНИЙ ---
BAD_WORDS = [
    "дурак", "какашка", "плохой", "маяк", "такси", "бублик", "собака",
    "строй", "купол", "подоконник", "сука", "осел", "козел", "пидор",
    "манда", "хуй", "сын шлюхи"
]

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    try:
        chat_id = message.chat.id
        text_lower = message.text.lower().strip()
        
        user_username = message.from_user.username
        user_username_lower = user_username.lower().strip() if user_username else ""
        target_my_username = MY_USERNAME.lower().strip()

        # Сохраняем данные в базу
        save_user(chat_id, user_username)
        save_message(chat_id, message.text)

        bot_info = bot.get_me()

        # ПРАВИЛО ОТВЕТА НА РЕПЛАЙ: Если ответили на сообщение бота — отвечаем ВСЕГДА
        if message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id:
            random_quote = get_random_message(chat_id)
            if random_quote:
                bot.reply_to(message, random_quote)
            else:
                bot.reply_to(message, "Я тебя слышу!")
            return

        # ПРОВЕРКА ДЛЯ ТЕБЯ (Команда "проверка")
        if text_lower == "проверка" and user_username_lower == target_my_username:
            bot.reply_to(message, "я тут❤️")
            return

        # ЛОГИКА ОТВЕТОВ ДЛЯ ТЕБЯ (Zanyal0x)
        if user_username_lower == target_my_username:
            if "я тебя люблю" in text_lower:
                bot.reply_to(message, "И я тебя люблю!!")
            return

        # ЛОГИКА ДЛЯ ВСЕХ ОСТАЛЬНЫХ В ГРУППЕ
        if message.chat.type in ['group', 'supergroup']:
            
            if "я тебя люблю" in text_lower:
                bot.reply_to(message, "Но общался со мной ты, а в законах твоих ноль")
                return

            has_bad_word = any(word in text_lower for word in BAD_WORDS)
            if has_bad_word:
                if random.randint(1, 3) == 1:
                    bot.reply_to(message, random.choice([
                        "Слышь, рот закрой",
                        "Пошли выйдем",
                        "Не общайся со мной так, а то закопаю тебя тут"
                    ]))
                return

            if "кто ты" in text_lower:
                bot.reply_to(message, "Я бот, созданный великим разработчиком!")
                return

            if random.randint(1, 10) == 1:
                random_quote = get_random_message(chat_id)
                if random_quote:
                    bot.reply_to(message, random_quote)
                return

    except Exception as e:
        print(f"Ошибка в обработчике: {e}")

# --- ЗАПУСК ПОТОКОВ ---
if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=spammer, daemon=True).start()
    
    print("Бот успешно обновлен и запущен!")
    bot.infinity_polling()
    
