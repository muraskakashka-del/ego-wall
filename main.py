import time
import telebot
from threading import Thread

# Твои данные
BOT_TOKEN = "8800501422:AAF20hiO_pNIyQm6qYfsQJqaYvI3r-kie7o"
GROUP_CHAT_ID = -1004358584205  # Обрати внимание: id группы должен быть числом, а не строкой

bot = telebot.TeleBot(BOT_TOKEN)

bot.remove_webhook()

# Функция для спама в ГРУППУ (300 секунд = 5 минут)
def spammer():
    while True:
        try:
            bot.send_message(GROUP_CHAT_ID, "го в мафию 🕵️‍♂️")
        except Exception as e:
            print(f"Ошибка спамера: {e}")
        time.sleep(300)

# Список оскорблений для проверки (все слова в нижнем регистре)
BAD_WORDS = [
    "дурак", "какашка", "плохой", "ишак", "эшек", "эщек", 
    "еблан", "сгейн", "тупой", "тупоголовый", "сука", 
    "осел", "козел", "пидор", "пидрила"
]

# Обработчик сообщений (ЛС и упоминания в группе)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    try:
        text_lower = message.text.lower() if message.text else ""
        
        # Проверяем, есть ли хоть одно оскорбление из списка в тексте сообщения
        has_bad_word = any(word in text_lower for word in BAD_WORDS)
        
        # Если оскорблений нет, то бот просто игнорирует сообщение
        if not has_bad_word:
            return

        if message.chat.type == 'private':
            bot.reply_to(message, "сам такой")
            
        elif message.chat.type in ['group', 'supergroup']:
            bot_username = bot.get_me().username.lower()
            
            is_reply = message.reply_to_message and message.reply_to_message.from_user.username.lower() == bot_username
            has_name = "марик" in text_lower or f"@{bot_username}" in text_lower
            
            # Бот ответит, только если его оскорбили (упомянули по имени/юзернейму или ответили на его сообщение)
            if is_reply or has_name:
                bot.reply_to(message, "сам такой")
                
    except Exception as e:
        print(f"Ошибка обработки: {e}")

if __name__ == "__main__":
    Thread(target=spammer, daemon=True).start()
    bot.infinity_polling()
    
