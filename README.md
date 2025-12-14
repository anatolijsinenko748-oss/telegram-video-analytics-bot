# Telegram-бот для аналитики видео по естественному языку

Бот, который по текстовому запросу на русском возвращает одно число из базы данных видео-статистики.

## Технологии

- Python 3.12
- PostgreSQL (в Docker)
- aiogram 3.x
- SQLAlchemy (async)
- Ollama + локальная LLM (llama3.1:8b или deepseek-coder:6.7b) для преобразования естественного языка в SQL
- Docker для базы данных

## Структура проекта
├── bot/                  # Код Telegram-бота
│   ├── main.py
│   ├── handlers.py
│   ├── database.py
│   ├── llm.py
│   └── prompts.py
├── data_loader.py        # Загрузка JSON в БД + применение миграций
├── migrations/           # SQL-миграции
│   └── create_tables.sql
├── docker-compose.yml    # PostgreSQL
├── requirements.txt
├── .gitignore
└── README.md

## Как запустить локально

### 1. Клонировать репозиторий и установить зависимости

```
git clone https://github.com/твой_логин/telegram-video-analytics-bot.git
cd telegram-video-analytics-bot
pip install -r requirements.txt 
```
### 2. Запустить PostgreSQL
```
docker-compose up -d
```
### 3. Загрузить данные 

Поместите предоставленный JSON-файл в корень проекта(или укажите путь)
```
python data_loader.py путь_к_файлу.json
```

### 4. Установите и запустите Ollama

- Скачайте с https://ollama.com/download
```
ollama pull llama3.1:8b   # или deepseek-coder:6.7b
```
- Запустите сервер Ollama и прогрейте модель один раз
```
ollama run llama3.1:8b
```

### 5. Настройте .env
Благодаря .gitignore он не попадет в проект, так как там находиться api моего бота
```
BOT_TOKEN=твой_токен_от_BotFather
OLLAMA_MODEL=llama3.1:8b   # или deepseek-coder:6.7b
```

### 6. Запустите бота
```
python -m bot.main
```
Бот готов принимать запросы и возвращать числовые ответы

## Архитектурный подход

- Пользователь пишет текст на русском
- llm.py отправляет запрос в локальную Ollama 
- LLM генерирует чистый SQL-запрос на основе детального промпта со схемой БД
- database.py выполняет SQL и возвращает одно значение 
- Бот отвечает только числом/строкой 

Контекст диалога не хранится - каждый диалог независимый
