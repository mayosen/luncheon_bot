# Ланч-бот
Бот для заказа еды из ресторана.

## Запуск
1. Установите зависимости
```
pip install -r requirements.txt
```
2. Создайте переменные среды (через терминал или IDE)
```
BOT_TOKEN = <Ваш Telegram токен>
ADMIN_PASSWORD = <Пароль администратора для бота>
DATABASE_URL = <Ссылка на базу данных>
// Пример ссылки: postgres://user:password@localhost:port/database
```
3. Создайте таблицы в базе данных, выполнив `database/models.py`

4. Запустите бота
```
python app.py
```

### Ссылки
[`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) library:  
- [Docs](https://python-telegram-bot.readthedocs.io/en/stable/index.html)
- [Examples](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md)
- [Code snippets](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets)  
- [Frequently requested design patterns](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Frequently-requested-design-patterns)
