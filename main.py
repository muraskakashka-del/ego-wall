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

# Раздельные базы данных для каждого чата в виде словарей
USER_POOLS = {}      # Формат: {chat_id: {сет_пользователей}}
MESSAGE_POOLS = {}   # Формат: {chat_id: [список_сообщений]}

# --- МИНИ ВЕБ-СЕРВЕР ДЛЯ ОБМАНА RENDER ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
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
        time.sleep(10)

BAD_WORDS = [
    "дурак", "какашка", "плохой", "ишак", "эшек", "эщек", 
    "еблан", "сгейн", "тупой", "тупоголовый", "сука", 
    "осел", "козел", "пидор", "пидрила", "сын шлюхи"
]

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    try:
        chat_id = message.chat.id
        text_lower = message.text.lower() if message.text else ""
        user_username = message.from_user.username.lower() if message.from_user.username else ""
        
        is_private = message.chat.type == 'private'
        is_group = message.chat.type in ['group', 'supergroup']
        bot_username = bot.get_me().username.lower()
        
        # Проверяем, является ли сообщение ответом (реплаем) именно на сообщение бота
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.username.lower() == bot_username

        # Инициализируем пустые базы данных для текущего чата, если их еще нет
        if chat_id not in USER_POOLS:
            USER_POOLS[chat_id] = set()
        if chat_id not in MESSAGE_POOLS:
            MESSAGE_POOLS[chat_id] = []

        # --- Персональная логика для тебя (zanyal0x) ---
        if user_username == "zanyal0x" and is_reply_to_bot:
            if "люблю" in text_lower:
                bot.reply_to(message, "я тебя тоже люблю\u2665\ufe0f\u2665\ufe0f")
            else:
                # На обычные реплаи без слова "люблю" бот теперь просто молчит
                pass
            return

        # Запоминаем сообщения СТРОГО для текущего чата
        if message.text and "могги кто" not in text_lower:
            MESSAGE_POOLS[chat_id].append(message.text)

        # Сохраняем пользователя СТРОГО для текущего чата
        if is_group and message.from_user:
            mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            USER_POOLS[chat_id].add(mention)

        has_name = False
        if is_group:
            has_name = "марик" in text_lower or f"@{bot_username}" in text_lower

        # Обработка команды "могги кто"
        if "могги кто" in text_lower:
            start_index = text_lower.find("могги кто") + len("могги "+ "кто")
            question = message.text[start_index:].strip()
            
            if not question:
                bot.reply_to(message, "После 'могги кто' нужно написать сам вопрос, например: 'могги кто дурак?'")
                return

            # Выбираем случайного юзера только из базы текущего чата chat_id
            if USER_POOLS[chat_id]:
                random_user = random.choice(list(USER_POOLS[chat_id]))
                bot.reply_to(message, f"я думаю что {random_user} {question}")
            else:
                bot.reply_to(message, f"я думаю что ты {question}")
            return

        # Ответы на триггеры, если это ЛС или упомянули/ответили боту в группе
        if is_private or (is_group and (is_reply_to_bot or has_name)):
            
            # Проверяем оскорбления
            has_bad_word = any(word in text_lower for word in BAD_WORDS)
            if has_bad_word:
                if user_username == "aikosha_099sa":
                    bot.reply_to(message, "айике ты меня обидела.")
                else:
                    rndm = random.randint(1,3)
                    if rndm == 1:
                        bot.reply_to(message, "сам такой")
                    elif rndm == 2:
                        bot.reply_to(message, "поешь пизды")
                    else:
                        bot.reply_to(message, "не общайся со мной так а то закопаю твою мать")
                return

            # Проверяем приветствие
            if "привет" in text_lower:
                bot.reply_to(message, "привет")
                return

            # Проверяем "как дела"
            if "как дела" in text_lower:
                bot.reply_to(message, "нормик")
                return

            # Рандомный ответ из чата (берем только цитаты текущего чата chat_id)
            if MESSAGE_POOLS[chat_id]:
                random_quote = random.choice(MESSAGE_POOLS[chat_id])
                bot.reply_to(message, random_quote)
            else:
                bot.reply_to(message, "Я пока запоминаю ваши сообщения... Поговорите еще!")
                
    except Exception as e:
        print(f"Ошибка обработки: {e}")

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    Thread(target=spammer, daemon=True).start()
    bot.infinity_polling()
    
