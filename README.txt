# Telegram Bot: Tic-Tac-Toe 🎮

Телеграм-бот для игры в крестики-нолики.  
Проект написан на Python с использованием библиотеки [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/username/tic-tac-toe-bot.git
cd tic-tac-toe-bot
```

### 2. Установка зависимостей
Рекомендуется использовать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

Установи зависимости:
```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации
В проекте есть файл `settings.py`.  
По умолчанию он выглядит так:
```python
import telebot

BOT_TOKEN = ""
ADMIN_ID = 0
ADMIN_GROUP = 0

bot = telebot.TeleBot(BOT_TOKEN)
```

#### ⚙️ Что нужно заполнить:
- `BOT_TOKEN` — токен твоего бота (получается у [@BotFather](https://t.me/BotFather))  
- `ADMIN_ID` — твой Telegram ID (узнать можно у [@userinfobot](https://t.me/userinfobot))  
- `ADMIN_GROUP` — ID группы/чата, куда бот может слать сообщения (отрицательное число для супергруппы)  

> ⚠️ Никогда не коммить токен в GitHub — используй пустые переменные в `config.py`, как сделано в этом репозитории.  

### 4. Запуск
```bash
python main.py
```

---

## 📜 Лицензия
Этот проект распространяется под лицензией **MIT**.  
Подробнее см. в файле [LICENSE](LICENSE).
