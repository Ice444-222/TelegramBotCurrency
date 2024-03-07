import asyncio
import configs
import requests
import locale
import math
from aiogram import F, Bot, Dispatcher, types
import logging
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown
from datetime import datetime,  timedelta
from curs_data import CURS_DATA, CB_ERROR, month_formatter, CURS_MOEX_DATA, day_deleter, check_moex, cb_date
from curs_data import MoexMethods

locale.setlocale(locale.LC_TIME, 'ru_RU')
bot = Bot(token=configs.TOKEN)
dp = Dispatcher()
valute_id = "GBP"
URL_CB = "https://www.cbr-xml-daily.ru/daily_json.js"
URL_MOEX = "https://iss.moex.com/iss/history/engines/currency/markets/index/boards/FIXI/securities.json?"
URL_MOEX_CHOISE = "https://iss.moex.com/iss/statistics/engines/futures/markets/indicativerates/securities/{}/RUB.json?from={}&till={}&iss.meta=off"

def get_curs_all():
    response_cb_all = requests.get(URL_CB)
    response_moex_all = requests.get(URL_MOEX)
    currency_data_cb_all =""
    currency_all_text = ""
    value_moex_final=""
    day_deleter_value = 1

    if response_cb_all.status_code == 200:
        data_cb_all = response_cb_all.json()
        currency_data_cb_all = data_cb_all.get("Valute", {})
        date_cb = cb_date(data_cb_all)
        currency_all_text = currency_all_text + f"Курс ЦБ актуален на {month_formatter(date_cb)}\n"

    for iterator in CURS_DATA:
        smile = CURS_DATA[iterator]['Emoji']
        name = CURS_DATA[iterator]['Name']
        try:
            nominal = currency_data_cb_all[iterator]["Nominal"]
            value_cb_raw = currency_data_cb_all[iterator]['Value']
            previous_cb_raw = currency_data_cb_all[iterator]['Previous']
            value_cb = math.floor(value_cb_raw / nominal * 100) / 100
            value_cb_diff = round((value_cb_raw - previous_cb_raw) / nominal, 3)
            value_cb_diff = str(value_cb_diff) + '💹' if value_cb_diff > 0 else str(value_cb_diff) + '🔻'
        except Exception:
            value_cb = "Не удалось загрузить данные"

                
        currency_all = f"{smile} {name}\n ЦБ {value_cb}({value_cb_diff})\n"
        currency_all_text = currency_all_text + currency_all
    
    return currency_all_text




def get_curs(currency):
    response = requests.get(URL_CB)
    
    if response.status_code == 200:
        data = response.json()
        currency_data = data.get("Valute", {}).get(currency)
        
        if currency_data:
            num_code = currency_data.get("NumCode")
            char_code = currency_data.get("CharCode")
            nominal = currency_data.get("Nominal")
            name = currency_data.get("Name")
            value = currency_data.get("Value")

            exchange_rate_info = f"NumCode: {num_code}\nCharCode: {char_code}\nNominal: {nominal}\nName: {name}\nValue: {value}"
            return exchange_rate_info

    return None

def get_on_start_kb():
    button_start_all = types.KeyboardButton(text='Показать все курсы валют!')
    button_start_curs = types.KeyboardButton(text='Выбрать интересующий курс')
    buttons_row_first = [button_start_all, button_start_curs]
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=[buttons_row_first], resize_keyboard=True)
    return keyboard

def curs_choice():
    buttons = []
    row = []
    for currency_code, data in CURS_DATA.items():
        button = types.KeyboardButton(text=f"{data['Emoji']} {data['Name']}")
        row.append(button)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    button_curs_back = types.KeyboardButton(text="В начало меню")
    buttons.append([button_curs_back])
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


@dp.message(CommandStart())
async def handle_start(message):
    await message.answer(text=f"Приветствую! Я бот для вывода актуального курса валют 🫡 ")
    await message.answer(text=f"Вы можете сделать запрос сразу по всем валютам чтобы увидеть актуальный курс ЦБ 👵")
    await message.answer(text=f"Также вы можете сделать запрос по конкретной валюте, посмотреть курс на конкретную дату и также увидеть курс Московской Биржы если данная валюта там торгуется. 🤑", reply_markup=get_on_start_kb())

@dp.message(F.photo)
async def handle_photo(message):
    await message.answer(text="bro whaat")

@dp.message(F.text == 'Показать все курсы валют!')
@dp.message(Command("curs_all"))
async def handle_curs(message):
    await message.answer(text=get_curs_all(), reply_markup=get_on_start_kb())

@dp.message(F.text == 'Выбрать интересующий курс')
@dp.message(Command("curs"))
async def handle_curs(message):
    await message.answer(text='Выбирайте!', reply_markup=curs_choice())

@dp.message(F.text == 'В начало меню')
@dp.message(Command("back"))
async def handle_start(message):
    await message.answer(text='Отправляю в начало меню...', reply_markup=get_on_start_kb())



async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

@dp.message(lambda message: any(f"{data['Emoji']} {data['Name']}" in message.text for data in CURS_DATA.values()))
async def handle_currency_choice(message: types.Message):
    currency_choise_text=''
    response_moex=''

    
    for currency_code, data in CURS_DATA.items():
        if data['Emoji'] == message.text.split(' ')[0]:
            currency_choise = currency_code
            response_cb_all = requests.get(URL_CB)
            if response_cb_all.status_code == 200:
                data_cb_all = response_cb_all.json()
                nominal = data_cb_all.get("Valute").get(currency_choise).get("Nominal")
                value_cb = data_cb_all.get("Valute").get(currency_choise).get('Value')
                value_cb_diff = round((value_cb / nominal - data_cb_all.get("Valute", {}).get(currency_choise).get('Previous') / nominal),5)
                if value_cb_diff > 0:
                    value_cb_diff = f"+{value_cb_diff}💹"
                else:
                    value_cb_diff = f"{value_cb_diff}🔻"
                date_cb = cb_date(data_cb_all)
                currency_choise_text = f"Курс Центробанка РФ:\n{value_cb}({value_cb_diff})\nУстановлен на:\n{month_formatter(date_cb)}\n"
            if data['MOEX'] == True:
                response_moex = MoexMethods.get_moex_repsonse(URL_MOEX_CHOISE, currency_choise)
                if response_moex.status_code == 200:
                    response_moex = response_moex.json()
                    last_element_value = response_moex.get("securities").get("data")[-1][3]
                    value_moex = response_moex.get("securities.current").get("data")[0][3]
                    if last_element_value == value_moex:
                        value_moex_prev = response_moex.get("securities").get("data")[-2][3]
                    else:
                        value_moex_prev = last_element_value
                    value_moex_diff = round(value_moex - value_moex_prev,5)
                    if value_moex_diff > 0:
                        value_moex_diff = f"+{value_moex_diff}💹"
                    else:
                        value_moex_diff = f"{value_moex_diff}🔻"
                    date_moex = response_moex.get("securities.current").get("data")[0][1]
                    time_moex = response_moex.get("securities.current").get("data")[0][2][:5]
                    moex_message = f"Курс Московской Биржи:\n{value_moex}({value_moex_diff})\nПоследнее обновление:\n{time_moex} мск {month_formatter(date_moex)}"
                else:
                    moex_message = 'Ошибка запроса данных Московской Биржи'
            else:
                moex_message = 'Валюта не продаётся на Московской Бирже.'
        
        
        
        
    await message.answer(f"{moex_message}\n\n{currency_choise_text}")

@dp.message()
async def echo_message(message):
    await message.answer(text='whadap')


asyncio.run(main())

