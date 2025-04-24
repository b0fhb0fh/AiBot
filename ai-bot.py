#!/usr/bin/python3

import telebot
from openai import OpenAI, APIConnectionError, APITimeoutError
import anthropic
import requests
import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

class AIChatBot:
    CONFIG_FILE = Path(__file__).parent / "config.json"
    LOG_FILE = Path(__file__).parent / "ai_bot.log"
    
    def __init__(self):
        """
        Инициализация бота с конфигурацией из файла config.json
        """
        self._setup_logging()
        self.config = self._load_config()
        self.bot = telebot.TeleBot(self.config['telegram_token'])
        self.ai_name = self.config.get('ai_name')
        self.ai_config = self.config.get('ai_config')
        
        # Инициализация клиента OpenAI, если указан ключ
        self.ai_client = None
        if str(self.ai_name).lower() == 'openai':
            self.ai_client = OpenAI(
                base_url=self.ai_config['base_url'],
                api_key=self.ai_config['api_key'],
                timeout=self.ai_config['timeout']
            )
        elif str(self.ai_name).lower() == 'anthropic':
            self.ai_client = anthropic.Anthropic(
                base_url=self.ai_config['base_url'],
                api_key=self.ai_config['api_key'],
                timeout=self.ai_config['timeout']
            )
        elif str(self.ai_name).lower() == 'ollama':
            # Ollama
            self.ai_client = "Ollama"
        else:
            self.logger.info(f"Указано некорректное имя модели {self.ai_name}.")
            sys.exit(1)
        
        # Регистрация обработчиков сообщений
        self._register_handlers()

    def _setup_logging(self):
        """Настройка системы логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _register_handlers(self):
        """Регистрация обработчиков сообщений"""
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self._send_welcome(message)
            
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            self._handle_message(message)

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
            
            # Проверка конфигурации ИИ
            ai_config = config.get('ai_config')
            if not ai_config.get('api_key'):
                raise ValueError("Должен быть указан api_key")
            
            return config
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {str(e)}")
            raise

    def ask_ai(self, prompt: str) -> str:
        """
        Отправляет запрос к ИИ (использует OpenAI, если доступен, иначе Ollama)
        """
        self.logger.info(f"Получен запрос: {prompt}")
        start_time = datetime.now()
        
        model = self.ai_config["model"]

        try:
            if str(self.ai_name).lower() == 'openai':
                response = self._ask_openai(prompt, model)
            elif str(self.ai_name).lower() == 'anthropic':
                response = self._ask_anthropic(prompt, model)
            else:
                response = self._ask_ollama(prompt, model)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Ответ получен за {duration:.2f} сек: {response}...")
            return response
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки запроса: {str(e)}", exc_info=True)
            return f"Произошла ошибка при обработке запроса: {str(e)}"

    def _ask_openai(self, prompt: str, model: str) -> str:
        """
        Отправляет запрос через OpenAI API
        """
        try:
            self.logger.debug(f"Отправка запроса к OpenAI API. Модель: {model}")
            
            chat_completion = self.ai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not chat_completion.choices:
                self.logger.warning("OpenAI не вернул ответа")
                return "ИИ не вернул ответа"
            
            response_message = chat_completion.choices[0].message
            response_content = response_message.content.strip() if response_message.content else "Пустой ответ от ИИ"
            
            self.logger.debug(f"Получен ответ от OpenAI: {response_content}...")
            return response_content
        
        except Exception as e:
            self.logger.error(f"Ошибка OpenAI API: {str(e)}", exc_info=True)
            raise

    def _ask_anthropic(self, prompt: str, model: str) -> str:
        """
        Отправляет запрос через Anthropic API
        """
        try:
            self.logger.debug(f"Отправка запроса к Anthropic API. Модель: {model}")
            
            message = self.ai_client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            if not message.content:
                self.logger.warning("Anthropic не вернул ответа")
                return "ИИ не вернул ответа"
            
            response_content = ""
            for content_block in message.content:
                if content_block.type == "text":
                    response_content += content_block.text
            
            if not response_content:
                response_content = "Пустой ответ от ИИ"
            else:
                response_content = response_content.strip()
            
            self.logger.debug(f"Получен ответ от Anthropic: {response_content[:200]}...")
            return response_content
        
        except Exception as e:
            self.logger.error(f"Ошибка Anthropic API: {str(e)}", exc_info=True)
            raise

    def _ask_ollama(self, prompt: str, model: str) -> str:
        """
        Отправляет запрос к локальному Ollama API
        """
        api_url = self.ai_config.get('ollama_api_url', 'http://localhost:11434/api/generate')
        payload = {
            "prompt": prompt,
            "model": model,
            "stream": False
        }
    
        headers = {
            'Content-Type': 'application/json',
            **self.ai_config.get('headers', {})
        }
    
        try:
            self.logger.debug(f"Отправка запроса к Ollama API. URL: {api_url}, Модель: {payload['model']}")
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=self.ai_config.get('timeout', 30)
            )
            response.raise_for_status()
            
            response_data = response.json()
            response_content = response_data.get("response", "Не получилось извлечь ответ из JSON")
            
            self.logger.debug(f"Получен ответ от Ollama: {response_content[:200]}...")
            return response_content
            
        except Exception as e:
            self.logger.error(f"Ошибка Ollama API: {str(e)}", exc_info=True)
            raise
    
    def _send_welcome(self, message):
        """Обработчик команд /start и /help"""
        self.logger.info(f"Обработка команды welcome от пользователя {message.from_user.id}")
        self.bot.reply_to(message, 
                         "Привет! Отправьте мне ваш вопрос, и я попробую на него ответить с помощью системы ИИ. "
                         "Для лучших результатов используйте английский язык.")

    def _handle_message(self, message):
        """Обработчик текстовых сообщений"""
        self.logger.info(f"Новое сообщение от {message.from_user.id} {message.from_user.username} {message.from_user.first_name} {message.from_user.last_name}: {message.text}")
        response = self.ask_ai(message.text)
        self.bot.reply_to(message, response[:4000])  # Ограничение длины сообщения в Telegram
        self.logger.info(f"Ответ отправлен пользователю {message.from_user.id}")

    def run(self):
        """Запуск бота с обработкой исключений"""
        self.logger.info("Запуск бота...")
        while True:
            try:
                self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
            except (APIConnectionError, APITimeoutError, ConnectionError) as e:
                self.logger.error(f"Ошибка подключения: {e}, перезапуск...")
                sys.stdout.flush()
                os.execv(sys.argv[0], sys.argv)

if __name__ == "__main__":
    try:
        bot = AIChatBot()
        bot.run()
    except Exception as e:
        print(f"Ошибка при запуске бота: {str(e)}")
        sys.exit(1)