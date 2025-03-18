#!/usr/bin/python3

import telebot
import requests

# Ваш токен от BotFather
TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# URL и конфигурация для запросов к OLLAMA (например, через HTTP)
OLLAMA_URL = "http://localhost:11434/api/generate"  # Замените PORT на правильный порт

def ask_ollama(prompt):
    """
    Отправляет запрос к OLLAMA и возвращает ответ.
    """
    response = requests.post(
        OLLAMA_URL,
        json={"prompt": prompt, "model": "llama3.2", "stream": False}
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Ошибка запроса к OLLAMA: {response.text}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправьте мне ваш вопрос, и я попробую на него ответить с помощью системы ИИ OLLAMA. Для общения лучше использовать английский язык.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """
    Обрабатывает текстовые сообщения от пользователей.
    """
    user_input = message.text
    response = ask_ollama(user_input)
    bot.reply_to(message, response)

# Запуск бота (с адекватным обработчиком исключений в продакшн-коде)
#bot.polling(none_stop=True)
########################################################################################################################
########################################################################################################################
########################################################################################################################
  
try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

########################################################################################################################
########################################################################################################################
########################################################################################################################
