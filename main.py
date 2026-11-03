
import time
import telebot
from threading import Thread

# Твои данные
BOT_TOKEN = "8800501422:AAF20hiO_pNIyQm6qYfsQJqaYvI3r-kie7o"
GROUP_CHAT_ID = -1004358584205

bot = telebot.TeleBot(BOT_TOKEN)

bot.remove_webhook()

# Функция для спама в ГРУППУ (300 секунд = 5 минут)
def spammer():
    while True:
        try:
            bot.send_message(GROUP_CHAT_ID, "го в мафию 🕵️‍♂️")
        except Exception as e:
            print(f"Ошибка спамера: {e}")
        time.sleep(0.1)

# Список оскорблений
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
        
        # Получаем юзернейм того, кто написал (в нижнем регистре для точности)
        user_username = message.from_user.username.lower() if message.from_user.username else ""
        
        # Переменные для определения, адресовано ли сообщение боту в группе
        is_private = message.chat.type == 'private'
        is_group = message.chat.type in ['group', 'supergroup']
        
        is_reply = False
        has_name = False
        
        if is_group:
            bot_username = bot.get_me().username.lower()
            is_reply = message.reply_to_message and message.reply_to_message.from_user.username.lower() == bot_username
            has_name = "марик" in text_lower or f"@{bot_username}" in text_lower

        # Бот реагирует, только если это ЛС ИЛИ его упомянули/ответили в группе
        if is_private or (is_group and (is_reply or has_name)):
            
            # 1. Проверяем на плохие слова
            has_bad_word = any(word in text_lower for word in BAD_WORDS)
            if has_bad_word:
                if user_username == "aikosha_099sa":
                    bot.reply_to(message, "айике ты меня обидела.")
                else:
                    bot.reply_to(message, "сам такой")
                return # Выходим, чтобы не проверять на другие фразы

            # 2. Проверяем на приветствие
            if "привет" in text_lower:
                bot.reply_to(message, "привет")
                return

            # 3. Проверяем на вопрос "как дела"
            if "как дела" in text_lower:
                bot.reply_to(message, "нормик")
                return
                
    except Exception as e:
        print(f"Ошибка обработки: {e}")

if __name__ == "__main__":
    Thread(target=spammer, daemon=True).start()
    bot.infinity_polling()
    
