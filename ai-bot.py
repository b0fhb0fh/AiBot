#!/usr/bin/python3

import telebot
import requests
import os
import sys
import json
from typing import Optional, Dict, Any
from pathlib import Path

class AIChatBot:
    CONFIG_FILE = Path(__file__).parent / "config.json"
    
    def __init__(self):
        """
        Инициализация бота с конфигурацией из файла config.json
        """
        self.config = self._load_config()
        self.bot = telebot.TeleBot(self.config['telegram_token'])
        self.ai_config = self.config.get('ai_config', {})
        
        # Регистрация обработчиков
        self.bot.message_handler(commands=['start', 'help'])(self.send_welcome)
        self.bot.message_handler(func=lambda message: True)(self.handle_message)

    def _load_config(self) -> Dict[str, Any]:
        """
        Загружает конфигурацию из файла config.json
        """
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Проверка обязательных параметров
            if not config.get('telegram_token'):
                raise ValueError("Не указан telegram_token в конфигурации")
            if not config.get('ai_config', {}).get('api_url'):
                raise ValueError("Не указан api_url в конфигурации ИИ")
                
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурационный файл {self.CONFIG_FILE} не найден")
        except json.JSONDecodeError:
            raise ValueError(f"Ошибка разбора JSON в файле {self.CONFIG_FILE}")

    def ask_ai(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Отправляет запрос к внешнему ИИ и возвращает ответ.
        """
        payload = {
            "prompt": prompt,
            "model": model or self.ai_config.get('model', 'llama3.2'),
            "stream": False
        }
        
        headers = self.ai_config.get('headers', {'Content-Type': 'application/json'})
        if 'api_key' in self.ai_config:
            headers['Authorization'] = f"Bearer {self.ai_config['api_key']}"
        
        try:
            response = requests.post(
                self.ai_config['api_url'],
                json=payload,
                headers=headers,
                timeout=self.ai_config.get('timeout', 30)
            )
            response.raise_for_status()
            return response.json().get("response", "Не получилось извлечь ответ из JSON")
        except requests.exceptions.RequestException as e:
            return f"Ошибка запроса к ИИ: {str(e)}"

    def send_welcome(self, message):
        """Обработчик команд /start и /help"""
        self.bot.reply_to(message, 
                         "Привет! Отправьте мне ваш вопрос, и я попробую на него ответить с помощью системы ИИ. "
                         "Для лучших результатов используйте английский язык.")

    def handle_message(self, message):
        """Обработчик текстовых сообщений"""
        response = self.ask_ai(message.text)
        self.bot.reply_to(message, response[:4000])  # Ограничение длины сообщения в Telegram

    def run(self):
        """Запуск бота с обработкой исключений"""
        while True:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
            except (ConnectionError, requests.exceptions.ReadTimeout) as e:
                sys.stdout.flush()
                os.execv(sys.argv[0], sys.argv)

if __name__ == "__main__":
    try:
        bot = AIChatBot()
        bot.run()
    except Exception as e:
        print(f"Ошибка при запуске бота: {str(e)}")
        sys.exit(1)
        