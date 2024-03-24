import asyncio
import configs
import re
import requests
import locale
from aiogram import F, Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime,  timedelta
from curs_data import month_formatter, day_deleter, check_moex, cb_date, is_valid_date
from curs_data import MoexMethods
import xml.etree.ElementTree as ET
from aiogram.filters import and_f, or_f
from routers import router as main_router
import keyboards.basic_keyboards as base_keyboard
import variables.constans as const

locale.setlocale(locale.LC_TIME, 'ru_RU')
storage = MemoryStorage()
bot = Bot(token=configs.TOKEN)
dp = Dispatcher()
dp.include_router(main_router)



class ClientState(StatesGroup):
    VALUTE = State()
    MAIN_MENU = State()
    DATE = State()
    CALC = State()
    RUB_TO_VAL = State()
    VAL_TO_RUB = State()
    







@dp.message(lambda message: any(re.search(r'\b{}\b'.format(re.escape(message.text.casefold())), data['Name'].casefold()) for data in const.CURS_DATA.values()))
@dp.message(lambda message: any(f"{data['Emoji']} {data['Name']}" in message.text for data in const.CURS_DATA.values()))
async def handle_currency_choice(message: types.Message, state: FSMContext):
    currency_choice_text = ''
    response_moex = ''
    moex_message = ''

    for currency_code, data in const.CURS_DATA.items():
        """
        Фильтр написан с учётом того что названия валют никак не пересекаются. Если планируется расширение списка валют c пересекающиемеся именами, нужно переписать фильтр"
        """
        if re.search(r'\b{}\b'.format(re.escape(message.text.casefold())), data['Name'].casefold()) or message.text.split()[0] in data['Emoji']:
            currency_choice = currency_code
            await state.set_state(ClientState.VALUTE)
            await state.update_data(VALUTE=currency_choice)
            await state.update_data(SYMBOL=data['Symbol'])
            try:
                response_cb_all = requests.get(const.URL_CB)
            except Exception:
                currency_choice_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
            if response_cb_all and response_cb_all.status_code == 200:
                data_cb_all = response_cb_all.json()
                nominal = data_cb_all.get("Valute").get(currency_choice).get("Nominal")
                value_cb = data_cb_all.get("Valute").get(currency_choice).get('Value')/nominal
                value_cb_prev = data_cb_all.get("Valute", {}).get(currency_choice).get('Previous') / nominal
                await state.update_data(VALUE_CB=value_cb)
                value_cb_diff = (value_cb - value_cb_prev)
                if value_cb_diff > 0:
                    smile = "💹"
                    sign = "+"
                else:
                    smile = "🔻"
                    sign = ""
                date_cb = cb_date(data_cb_all)
                currency_choice_text = f"Курс Центробанка РФ:\n{round(value_cb,3)}({sign}{round(value_cb_diff,5)}{smile})\nУстановлен на:\n{month_formatter(date_cb)}\n"
            else:
                currency_choice_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
            if data['MOEX'] == True:
                try:
                    response_moex = MoexMethods.get_moex_repsonse(const.URL_MOEX_CHOICE, currency_choice)
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

    await message.answer(text=f"{moex_message}\n\n{currency_choice_text}", reply_markup=base_keyboard.curs_choice_result_kb(ClientState.VALUTE))


@dp.message(and_f(or_f(ClientState.VALUTE, ClientState.CALC), F.text == 'Показать курс на конкретную дату'))
async def handle_curs_date_response(message, state):
    await state.set_state(ClientState.DATE)
    await message.answer(text='Пожалуйста, введите требуемую дату в следующем формате: дд.мм.гггг', reply_markup=base_keyboard.curs_choice_result_kb(ClientState.DATE))


@dp.message(F.text == 'Назад к выбору валюты')
async def handle_curs_date_response(message):
    await message.answer(text="Отправляю назад.", reply_markup=base_keyboard.curs_choice_kb())





@dp.message(ClientState.DATE,)
async def handle_curs_date_response(message, state):
    user_input = message.text
    if is_valid_date(user_input):
        user_input_slash = user_input.replace('.', '/')
        valute_data = await state.get_data()
        user_choice = valute_data['VALUTE']
        value_cb = valute_data['VALUE_CB']
        url_find = ("./Valute[CharCode='{}']/VunitRate").format(user_choice)
        url_request = (const.URL_CB_DATE).format(user_input_slash)
        await state.update_data(selected_date=user_input_slash)
        try:
            response_cb_all = float(ET.fromstring(requests.get(url_request).text).find(url_find).text.replace(',', '.'))
            difference = int(round(((value_cb*1000)/(response_cb_all*1000)-1)*100, 0))
            difference_text = "C данной даты курс {} на {}%{}"
            if difference > 0:
                result = 'увеличился'
                smile = "💹"
            elif difference < 0:
                result = 'уменьшился'
                difference *= -1
                smile = "🔻"
            else:
                difference_text = 'курс не изменился'
            await message.answer(f"Курс на {user_input}: {response_cb_all}\n{difference_text.format(result,difference,smile)}")
        except Exception:
            await message.answer("Нету данных ЦБ РФ на данную дату, возможно на тот момент ЦБ РФ ещё указывал курс для данной валюты. Попробуйте указать более позднюю дату.")
    else:
        await message.answer("Извините, формат некорректен. Введите дату в формате дд.мм.гггг.\nНапример 05.12.2006")





@dp.message(or_f(ClientState.VAL_TO_RUB, ClientState.RUB_TO_VAL))
async def handle_curs_date_response(message, state):
    current_state = await state.get_state()
    valute_data = await state.get_data()
    value_cb = valute_data['VALUE_CB']
    symbol = valute_data['SYMBOL']
    text_without_commas = message.text.replace(',', '.')
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
        value = "Введите пожалуйста только целое или дробное число."
    await message.answer(text=f"{text_without_commas}{main_symbol} это {round(value,2)}{second_symbol}", reply_markup=base_keyboard.curs_calculator_kb(current_state))


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

asyncio.run(main())

