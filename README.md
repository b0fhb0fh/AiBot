# MyAiBot
проба пера - телеграм-бот, делающий запросы к AI

1. скачать и проинсталлировать ollama отсюда https://ollama.com/download

2. выбрать модель для использования

ollama pull "model"

рекомендую llama3.2 или phi4

указать модель в config.json

4. Проинсталлировать библиотеки

pip install -r requirements.txt

5. в BotFather запустить /newbot и получить для него token

указать этот токен в config.json

6. необходимо запустить ollama

ollama run <model> 

7. запустить бот

nohup python3 ai-bot.py &

или

screen -d -m python3 ai-bot.py
