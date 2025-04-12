```markdown
# Telegram AI Chat Bot

Бот для Telegram, который отвечает на вопросы пользователей, используя внешний ИИ (например, Ollama, OpenAI или другие совместимые API).

## Особенности

- Поддержка различных моделей ИИ через API
- Конфигурация через файл `config.json`
- Автоматический перезапуск при ошибках соединения
- Ограничение длины сообщений для соответствия лимитам Telegram

## Требования

- Python 3.7+
- Установленные зависимости из `requirements.txt`

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/telegram-ai-bot.git
   cd telegram-ai-bot
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Создайте файл конфигурации `config.json` (см. пример ниже)

## Конфигурация

Создайте файл `config.json` в корневой директории проекта:

```json
{
    "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "ai_config": {
        "api_url": "http://localhost:11434/api/generate",
        "model": "llama3.2",
        "api_key": "your_api_key_optional",
        "timeout": 30,
        "headers": {
            "Content-Type": "application/json"
        }
    }
}
```

### Параметры конфигурации

- `telegram_token` - обязательный, токен вашего Telegram бота от @BotFather
- `ai_config` - настройки для подключения к API ИИ:
  - `api_url` - обязательный, URL endpoint API
  - `model` - модель ИИ по умолчанию
  - `api_key` - опциональный API ключ (если требуется)
  - `timeout` - таймаут запроса в секундах (по умолчанию 30)
  - `headers` - дополнительные заголовки HTTP запроса

## Запуск бота

```bash
python3 bot.py
```

## Использование

1. Начните чат с ботом в Telegram
2. Отправьте команду `/start` или `/help` для получения приветственного сообщения
3. Отправьте любой текст - бот ответит с помощью подключенного ИИ

## Поддерживаемые API

Бот может работать с любым API ИИ, которое поддерживает:
- POST запросы
- JSON формат запроса/ответа
- Аналогичную Ollama структуру запроса

Примеры совместимых сервисов:
- Ollama (локально или на сервере)
- OpenAI API
- Anthropic Claude API
- Google Gemini API (с соответствующей настройкой)

## Доработка

Чтобы адаптировать бота под конкретный API:
1. Измените структуру запроса в методе `ask_ai` класса `AIChatBot`
2. Настройте соответствующие параметры в `config.json`

## Лицензия

MIT License
```
