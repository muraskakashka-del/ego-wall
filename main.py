import time
import telebot
import random
from threading import Thread

# Твои данные
BOT_TOKEN = "ТВОЙ_ОБНОВЛЕННЫЙ_ТОКЕН_БОТА"
GROUP_CHAT_ID = -1004358584205

bot = telebot.TeleBot(BOT_TOKEN)

bot.remove_webhook()

# Список для сохранения активных участников группы (чтобы было из кого выбирать)
# Хранит кортежи вида (username, first_name)
USER_POOL = set()

# Функция для спама в ГРУППУ (300 секунд = 5 минут)
def spammer():
    while True:
        try:
            bot.send_message(GROUP_CHAT_ID, "го в мафию 🕵️‍♂️")
        except Exception as e:
            print(f"Ошибка спамера: {e}")
        time.sleep(600)

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
        user_username = message.from_user.username.lower() if message.from_user.username else ""
        
        is_private = message.chat.type == 'private'
        is_group = message.chat.type in ['group', 'supergroup']
        
        # Если пишут в группе, запоминаем пользователя для интерактива "могги кто..."
        if is_group and message.from_user:
            mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            USER_POOL.add(mention)

        is_reply = False
        has_name = False
        
        if is_group:
            bot_username = bot.get_me().username.lower()
            is_reply = message.reply_to_message and message.reply_to_message.from_user.username.lower() == bot_username
            has_name = "марик" in text_lower or f"@{bot_username}" in text_lower

        # Сначала проверяем глобальную команду "могги кто", для неё не обязательно тегать бота
        if "могги кто" in text_lower:
            # Находим, где заканчивается фраза "могги кто"
            start_index = text_lower.find("могги кто") + len("могги кто")
            question = message.text[start_index:].strip() # Вырезаем сам вопрос с оригинальным регистром
            
            if not question:
                bot.reply_to(message, "После 'могги кто' нужно написать сам вопрос, например: 'могги кто дурак?'")
                return

            if USER_POOL:
                # Выбираем случайного чела из тех, кого бот запомнил
                random_user = random.choice(list(USER_POOL))
                bot.reply_to(message, f"я думаю что {random_user} {question}")
            else:
                # На случай, если бот только запустился и еще никто не успел ничего написать
                bot.reply_to(message, f"я думаю что ты {question}")
            return

        # Бот реагирует на остальное, только если это ЛС ИЛИ его упомянули/ответили в группе
        if is_private or (is_group and (is_reply or has_name)):
            
            # 1. Проверяем на плохие слова
            has_bad_word = any(word in text_lower for word in BAD_WORDS)
            if has_bad_word:
                if user_username == "aikosha_099sa":
                    bot.reply_to(message, "айике ты меня обидела.")
                else:
                    bot.reply_to(message, "сам такой")
                return

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
    
