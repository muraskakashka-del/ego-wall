import time
import os
import random
import threading
import sqlite3
from telebot import TeleBot
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8800501422:AAF20hiO_pNIyQm6qYfsQJqaYvI3r-kie7o"
GROUP_CHAT_ID = -1004358584206
MY_USERNAME = "zanyalox"  # Твой юзернейм

bot = TeleBot(BOT_TOKEN)
bot.remove_webhook()

# --- РАБОТА С БАЗОЙ ДАННЫХ (SQLite) ---
DB_FILE = "bot_data.db"

def init_db():
    """Создает таблицы, если они еще не созданы."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Таблица для хранения сообщений чата (для рандомного спама и ответов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            text TEXT
        )
    ''')
    # Таблица для хранения уникальных пользователей чата
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
    """Сохраняет сообщение в базу данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (chat_id, text) VALUES (?, ?)", (chat_id, text))
    conn.commit()
    conn.close()

def get_random_message(chat_id):
    """Берет случайное сохраненное сообщение для конкретного чата."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM messages WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_messages_count(chat_id):
    """Считает сколько всего сообщений в базе для чата."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def save_user(chat_id, username):
    """Сохраняет пользователя, если его еще нет."""
    if not username:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)", (chat_id, username.lower()))
    conn.commit()
    conn.close()

def get_random_user(chat_id):
    """Выбирает случайного пользователя из чата."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Инициализируем БД при старте скрипта
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


# --- АВТОМАТИЧЕСКИЙ СПАМ КАЖДЫЙ ЧАС С РАНДОМНЫМ ЗАДЕРЖАНИЕМ ---
def spammer():
    while True:
        try:
            # Каждый час выбираем случайное время задержки от 1 до 3600 секунд
            delay = random.randint(1, 3600)
            print(f"[Спамер] Следующее сообщение будет отправлено через {delay} сек.")
            time.sleep(delay)
            
            # Пытаемся взять случайное сообщение из базы данных
            text_to_send = get_random_message(GROUP_CHAT_ID)
            
            if text_to_send:
                bot.send_message(GROUP_CHAT_ID, text_to_send)
                print(f"[Спамер] Отправлено: {text_to_send}")
            else:
                # Если база данных пустая, отправляем дефолтную фразу
                bot.send_message(GROUP_CHAT_ID, "Я за вами слежу 👁")
            
            # Дожидаемся остатка часа, чтобы цикл четко повторялся раз в 3600 секунд
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
        text_lower = message.text.lower()
        
        # Получаем юзернейм автора сообщения
        user_username = message.from_user.username
        user_username_lower = user_username.lower() if user_username else ""

        # Сохраняем пользователя и текст в постоянную базу SQLite
        save_user(chat_id, user_username)
        save_message(chat_id, message.text)

        # 1. Твоя секретная команда «проверка»
        if text_lower == "проверка" and user_username_lower == MY_USERNAME.lower():
            bot.reply_to(message, "я тут❤️")
            return

        # 2. Обработка ответов персонально для тебя (zanyalox)
        if user_username_lower == MY_USERNAME.lower():
            if "я тебя люблю" in text_lower:
                bot.reply_to(message, "И я тебя люблю!!")
                return
            # Если ты написал что-то другое, бот просто молчит, как ты и просил
            return

        # 3. Логика для всех остальных пользователей группы
        if message.chat.type in ['group', 'supergroup']:
            
            # Если кто-то чужой пишет «я тебя люблю»
            if "я тебя люблю" in text_lower:
                bot.reply_to(message, "Но общался со мной ты, а в законах твоих ноль")
                return

            # Проверка матов
            has_bad_word = any(word in text_lower for word in BAD_WORDS)
            if has_bad_word:
                # 33% шанс ответить жестко на мат
                if random.randint(1, 3) == 1:
                    bot.reply_to(message, random.choice([
                        "Слышь, рот закрой",
                        "Пошли выйдем",
                        "Не общайся со мной так, а то закопаю тебя тут"
                    ]))
                return

            # Обработка вопроса «кто ты»
            if "кто ты" in text_lower:
                bot.reply_to(message, "Я бот, созданный великим разработчиком!")
                return

            # Шанс 1 из 10 ответить случайным сохраненным сообщением
            if random.randint(1, 10) == 1:
                random_quote = get_random_message(chat_id)
                if random_quote:
                    bot.reply_to(message, random_quote)
                return

    except Exception as e:
        print(f"Ошибка в обработчике: {e}")


# --- ЗАПУСК ПОТОКОВ ---
if __name__ == "__main__":
    # Поток веб-сервера для Render
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Поток ежечасного рандомного спамера
    threading.Thread(target=spammer, daemon=True).start()
    
    # Основной поток бота
    print("Бот успешно запущен и готов к работе!")
    bot.infinity_polling()
