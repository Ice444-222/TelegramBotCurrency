# Инструкция по запуска бота по отслеживанию валюты


## Как запустить бота: 

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Ice444-222/TelegramBotCurrency.git
```

Создать и активировать виртуальное окружение

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости
```
pip install -r requirements.txt
```

Создать в папке проекта файл configs.py и добавить следующие данные:

```
TOKEN = '' # Токен вашего бота Telegram
```

Запустить файл бота
```
python3 main.py
```


## Инструкции по работе

Бот доступен в телеграмм по ссылке https://t.me/AnzhelaKhegde_registration_bot

Для начала работы нужны выполнить компанду /start

В дальнейшем нужно пользоваться встроенной клавиатурой

Бот отслеживает курс ЦБ и Московской биржи

В боте есть калькулятор и показ курса на определённую дату


