import time
import telebot
import random
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Твои данные
BOT_TOKEN = "8800501422:AAF20hiO_pNIyQm6qYfsQJqaYvI3r-kie7o"
GROUP_CHAT_ID = -1004358584205

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()

USER_POOL = set()

# --- МИНИ ВЕБ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    # Render сам передает порт в переменные окружения, если его нет — берем 8080
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), WebServerHandler)
    print(f"Запуск фейк-сервера на порту {port}...")
    server.serve_forever()
# ------------------------------------------

def spammer():
    while True:
        try:
            bot.send_message(GROUP_CHAT_ID, "го в мафию 🕵️‍♂️")
        except Exception as e:
            print(f"Ошибка спамера: {e}")
        time.sleep(1)

BAD_WORDS = [
    "дурак", "какашка", "плохой", "ишак", "эшек", "эщек", 
    "еблан", "сгейн", "тупой", "тупоголовый", "сука", 
    "осел", "козел", "пидор", "пидрила"
]

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    try:
        text_lower = message.text.lower() if message.text else ""
        user_username = message.from_user.username.lower() if message.from_user.username else ""
        
        is_private = message.chat.type == 'private'
        is_group = message.chat.type in ['group', 'supergroup']
        
        if is_group and message.from_user:
            mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            USER_POOL.add(mention)

        is_reply = False
        has_name = False
        
        if is_group:
            bot_username = bot.get_me().username.lower()
            is_reply = message.reply_to_message and message.reply_to_message.from_user.username.lower() == bot_username
            has_name = "марик" in text_lower or f"@{bot_username}" in text_lower

        if "могги кто" in text_lower:
            start_index = text_lower.find("могги кто") + len("могги кто")
            question = message.text[start_index:].strip()
            
            if not question:
                bot.reply_to(message, "После 'могги кто' нужно написать сам вопрос, например: 'могги кто дурак?'")
                return

            if USER_POOL:
                random_user = random.choice(list(USER_POOL))
                bot.reply_to(message, f"я думаю что {random_user} {question}")
            else:
                bot.reply_to(message, f"я думаю что ты {question}")
            return

        if is_private or (is_group and (is_reply or has_name)):
            has_bad_word = any(word in text_lower for word in BAD_WORDS)
            if has_bad_word:
                if user_username == "aikosha_099sa":
                    bot.reply_to(message, "айике ты меня обидела.")
                else:
                    bot.reply_to(message, "сам такой")
                return

            if "привет" in text_lower:
                bot.reply_to(message, "привет")
                return

            if "как дела" in text_lower:
                bot.reply_to(message, "нормик")
                return
                
    except Exception as e:
        print(f"Ошибка обработки: {e}")

if __name__ == "__main__":
    # Запускаем фейковый веб-сервер в отдельном потоке, чтобы Render был доволен
    Thread(target=run_web_server, daemon=True).start()
    # Запускаем спамер
    Thread(target=spammer, daemon=True).start()
    # Запускаем бота
    bot.infinity_polling()
    
