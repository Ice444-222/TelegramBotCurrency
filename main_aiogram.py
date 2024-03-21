import asyncio
import configs
import re
import requests
import locale
import math
from aiogram import F, Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime,  timedelta
from curs_data import CURS_DATA, CB_ERROR, month_formatter, CURS_MOEX_DATA, day_deleter, check_moex, cb_date, is_valid_date
from curs_data import MoexMethods
import xml.etree.ElementTree as ET
from aiogram.filters import and_f, or_f

locale.setlocale(locale.LC_TIME, 'ru_RU')
storage = MemoryStorage()
bot = Bot(token=configs.TOKEN)
dp = Dispatcher()
valute_id = "GBP"
URL_CB = "https://www.cbr-xml-daily.ru/daily_json.js"
URL_CB_DATE = "https://www.cbr.ru/scripts/XML_daily.asp?date_req={}"
URL_MOEX = "https://iss.moex.com/iss/history/engines/currency/markets/index/boards/FIXI/securities.json?"
URL_MOEX_CHOISE = "https://iss.moex.com/iss/statistics/engines/futures/markets/indicativerates/securities/{}/RUB.json?from={}&till={}&iss.meta=off"

class ClientState(StatesGroup):
    VALUTE = State()
    MAIN_MENU = State()
    DATE = State()
    CALC = State()
    RUB_TO_VAL = State()
    VAL_TO_RUB = State()
    




def get_on_start_kb():
    button_start_all = types.KeyboardButton(text='Показать все курсы валют!')
    button_start_choise = types.KeyboardButton(text='Выбрать интересующий курс')
    buttons_row_first = [button_start_all, button_start_choise]
    keyboard = types.ReplyKeyboardMarkup(keyboard=[buttons_row_first], resize_keyboard=True)
    return keyboard

def curs_calculator_kb(current_state):
    button_calc_back = types.KeyboardButton(text='Назад к выбору валюты')
    button_calc_menu = types.KeyboardButton(text='В главное меню')
    button_calc_percent = types.KeyboardButton(text='Прибавь 1% к курсу ЦБ!')
    button_calc_date = types.KeyboardButton(text='Показать курс на конкретную дату')
    buttons_row_first = []
    buttons_row_second = [button_calc_percent, button_calc_date]
    buttons_row_third = [button_calc_back, button_calc_menu]
    if current_state != ClientState.RUB_TO_VAL:
        button_calc_ruble_to_valute = types.KeyboardButton(text='Переведи рубли в валюту')
        buttons_row_first.append(button_calc_ruble_to_valute)
    if current_state != ClientState.VAL_TO_RUB:
        button_calc_valute_to_ruble = types.KeyboardButton(text='Переведи валюту в рубли')
        buttons_row_first.append(button_calc_valute_to_ruble)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[buttons_row_first, buttons_row_second, buttons_row_third], resize_keyboard=True)
    return keyboard

def curs_choice_kb():
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
    button_choise_menu = types.KeyboardButton(text="В главное меню")
    buttons.append([button_choise_menu])
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def curs_choise_result_kb(current_state):
    button_choise_result_back = types.KeyboardButton(text='Назад к выбору валюты')
    button_choise_result_menu = types.KeyboardButton(text='В главное меню')
    button_choise_result_calc = types.KeyboardButton(text='Калькулятор')
    buttons_row_first = [button_choise_result_back, button_choise_result_menu]
    buttons_row_second = [button_choise_result_calc]
    if current_state == ClientState.VALUTE:
        button_choise_result_date = types.KeyboardButton(text='Показать курс на конкретную дату')
        buttons_row_second.append(button_choise_result_date)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[buttons_row_first, buttons_row_second], resize_keyboard=True)
    return keyboard

def get_curs_all():
    try:
        response_cb_all = requests.get(URL_CB)
    except Exception:
        currency_all_text = "Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже"
    currency_data_cb_all =""
    currency_all_text = ""

    if response_cb_all and response_cb_all.status_code == 200:
        data_cb_all = response_cb_all.json()
        currency_data_cb_all = data_cb_all.get("Valute", {})
        date_cb = cb_date(data_cb_all)
        currency_all_text = currency_all_text + f"Курс ЦБ актуален на {month_formatter(date_cb)}\n"
    else:
        currency_all_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'

    for iterator in CURS_DATA:
        smile = CURS_DATA[iterator]['Emoji']
        name = CURS_DATA[iterator]['Name']
        try:
            nominal = currency_data_cb_all[iterator]["Nominal"]
            value_cb = currency_data_cb_all[iterator]['Value'] / nominal
            previous_cb = currency_data_cb_all[iterator]['Previous'] / nominal
            value_cb_diff = value_cb - previous_cb
            value_cb_diff = str(value_cb_diff) + '💹' if value_cb_diff > 0 else str(value_cb_diff) + '🔻'
        except Exception:
            value_cb = "Не удалось загрузить данные"

                
        currency_all = f"{smile} {name}\n ЦБ {round(value_cb,2)}({value_cb_diff})\n"
        currency_all_text = currency_all_text + currency_all
    
    return currency_all_text



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
    await message.answer(text='Выбирайте!', reply_markup=curs_choice_kb())

@dp.message(F.text == 'В главное меню')
@dp.message(Command("back"))
async def handle_start(message, state):
    await state.set_state(ClientState.MAIN_MENU)
    await message.answer(text='Отправляю в главное меню...', reply_markup=get_on_start_kb())

@dp.message(lambda message: any(re.search(r'\b{}\b'.format(re.escape(message.text.casefold())), data['Name'].casefold()) for data in CURS_DATA.values()))
@dp.message(lambda message: any(f"{data['Emoji']} {data['Name']}" in message.text for data in CURS_DATA.values()))
async def handle_currency_choice(message: types.Message, state: FSMContext):
    currency_choise_text=''
    response_moex=''
    moex_message=''

    
    for currency_code, data in CURS_DATA.items():
        if re.search(r'\b{}\b'.format(re.escape(message.text.casefold())), data['Name'].casefold()) or message.text.split()[0] in data['Emoji']:
            currency_choise = currency_code
            await state.set_state(ClientState.VALUTE)
            await state.update_data(VALUTE=currency_choise)
            await state.update_data(SYMBOL=data['Symbol'])
            try:
                response_cb_all = requests.get(URL_CB)
            except Exception:
                currency_choise_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
            if response_cb_all and response_cb_all.status_code == 200:
                data_cb_all = response_cb_all.json()
                nominal = data_cb_all.get("Valute").get(currency_choise).get("Nominal")
                value_cb = data_cb_all.get("Valute").get(currency_choise).get('Value')/nominal
                value_cb_prev = data_cb_all.get("Valute", {}).get(currency_choise).get('Previous') / nominal
                await state.update_data(VALUE_CB=value_cb)
                value_cb_diff = (value_cb - value_cb_prev)
                if value_cb_diff > 0:
                    smile = "💹"
                    sign = "+"
                else:
                    smile = "🔻"
                    sign = ""
                date_cb = cb_date(data_cb_all)
                currency_choise_text = f"Курс Центробанка РФ:\n{round(value_cb,3)}({sign}{round(value_cb_diff,5)}{smile})\nУстановлен на:\n{month_formatter(date_cb)}\n"
            else:
                currency_choise_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
            if data['MOEX'] == True:
                try:
                    response_moex = MoexMethods.get_moex_repsonse(URL_MOEX_CHOISE, currency_choise)
                except Exception:
                    moex_message = 'Не удалось получить данные по курсу Московской биржи, попробуйте сделать запрос позже (бывает достаточно отправить ещё один запрос)'
                if response_moex and response_moex.status_code == 200:
                    response_moex = response_moex.json()
                    last_element_value = response_moex.get("securities").get("data")[-1][3]
                    value_moex = response_moex.get("securities.current").get("data")[0][3]
                    if last_element_value == value_moex:
                        value_moex_prev = response_moex.get("securities").get("data")[-2][3]
                    else:
                        value_moex_prev = last_element_value
                    value_moex_diff = value_moex - value_moex_prev
                    if value_moex_diff > 0:
                        smile = "💹"
                        sign = "+"
                    else:
                        smile = "🔻"
                        sign = ""
                    date_moex = response_moex.get("securities.current").get("data")[0][1]
                    time_moex = response_moex.get("securities.current").get("data")[0][2][:5]
                    moex_message = f"Курс Московской Биржи:\n{round(value_moex,3)}({sign}{round(value_moex_diff,5)}{smile})\nПоследнее обновление:\n{time_moex} мск {month_formatter(date_moex)}"
                else:
                    moex_message = 'Не удалось получить данные по курсу Московской биржи, попробуйте сделать запрос позже (бывает достаточно отправить ещё один запрос)'
            else:
                moex_message = 'Валюта не продаётся на Московской Бирже.'

    await message.answer(text=f"{moex_message}\n\n{currency_choise_text}", reply_markup=curs_choise_result_kb(ClientState.VALUTE))

@dp.message(and_f(or_f(ClientState.VALUTE, ClientState.CALC), F.text == 'Показать курс на конкретную дату'))
async def handle_curs_date_response(message, state):
    await state.set_state(ClientState.DATE)
    await message.answer(text='Пожалуйста, введите требуемую дату в следующем формате: дд.мм.гггг', reply_markup=curs_choise_result_kb(ClientState.DATE))

@dp.message(F.text == 'Назад к выбору валюты')
async def handle_curs_date_response(message):
    await message.answer(text="Отправляю назад.", reply_markup=curs_choice_kb())

@dp.message (and_f(or_f(ClientState.VALUTE, ClientState.DATE), F.text == 'Калькулятор'))
async def handle_curs_date_response(message, state):
    await state.set_state(ClientState.CALC)
    await message.answer(text="Считаю", reply_markup=curs_calculator_kb(ClientState.CALC))

@dp.message(ClientState.DATE,)
async def handle_curs_date_response(message, state):
    user_input = message.text
    if is_valid_date(user_input):
        user_input_slash=user_input.replace('.','/')
        valute_data = await state.get_data()
        user_choise = valute_data['VALUTE']
        value_cb = valute_data['VALUE_CB']
        url_find = ("./Valute[CharCode='{}']/VunitRate").format(user_choise)
        url_request = (URL_CB_DATE).format(user_input_slash)
        await state.update_data(selected_date=user_input_slash)
        try:
            response_cb_all = float(ET.fromstring(requests.get(url_request).text).find(url_find).text.replace(',','.'))
            difference = int(round(((value_cb*1000)/(response_cb_all*1000)-1)*100,0))
            difference_text = "C данной даты курс {} на {}%{}"
            if difference > 0:
                result = 'увеличился'
                smile="💹"
            elif difference < 0:
                result = 'уменьшился'
                difference*=-1
                smile="🔻"
            else:
                difference_text = 'курс не изменился'
            await message.answer(f"Курс на {user_input}: {response_cb_all}\n{difference_text.format(result,difference,smile)}")
        except Exception:
            await message.answer("Нету данных ЦБ РФ на данную дату, возможно на тот момент ЦБ РФ ещё указывал курс для данной валюты. Попробуйте указать более позднюю дату.")
    else:
        await message.answer("Извините, формат некорректен. Введите дату в формате дд.мм.гггг.\nНапример 05.12.2006")

@dp.message(and_f(or_f(ClientState.CALC, ClientState.VAL_TO_RUB, ClientState.RUB_TO_VAL), F.text == 'Прибавь 1% к курсу ЦБ!'))
async def handle_curs_date_response(message, state):
    await state.set_state(ClientState.CALC)
    valute_data = await state.get_data()
    value_cb = valute_data['VALUE_CB']
    value_percent = value_cb*101/100
    await message.answer(text=f"Готово! {value_cb} => {round(value_percent,4)}", reply_markup=curs_calculator_kb(ClientState.CALC))

@dp.message(and_f(or_f(ClientState.CALC, ClientState.RUB_TO_VAL), F.text == 'Переведи валюту в рубли'))
async def handle_curs_date_response(message, state):
    await state.set_state(ClientState.VAL_TO_RUB)
    await message.answer(text=f"Введите количество валюты", reply_markup=curs_calculator_kb(ClientState.VAL_TO_RUB))

@dp.message(and_f(or_f(ClientState.CALC, ClientState.VAL_TO_RUB), F.text == 'Переведи рубли в валюту'))
async def handle_curs_date_response(message, state):
    await state.set_state(ClientState.RUB_TO_VAL)
    await message.answer(text=f"Введите количество рублей", reply_markup=curs_calculator_kb(ClientState.RUB_TO_VAL))

@dp.message(or_f(ClientState.VAL_TO_RUB,ClientState.RUB_TO_VAL))
async def handle_curs_date_response(message, state):
    current_state = await state.get_state()
    valute_data = await state.get_data()
    value_cb = valute_data['VALUE_CB']
    symbol = valute_data['SYMBOL']
    text_without_commas = message.text.replace(',','.')
    if text_without_commas.isdigit() or text_without_commas.replace('.', '', 1).isdigit():
        if current_state == ClientState.VAL_TO_RUB:
            value = float(text_without_commas) * value_cb
            main_symbol = symbol
            second_symbol = '₽'
        else:
            value = float(text_without_commas) / value_cb
            main_symbol = '₽'
            second_symbol = symbol   
    else:
        value = f"Введите пожалуйста только целое или дробное число."
    await message.answer(text=f"{text_without_commas}{main_symbol} это {round(value,2)}{second_symbol}", reply_markup=curs_calculator_kb(current_state))




async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

asyncio.run(main())

