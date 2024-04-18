import variables.states as st
from aiogram import Router, F
from curs_data import is_valid_date
import variables.constans as const
import xml.etree.ElementTree as ET
import requests
from aiogram.filters import and_f, or_f
import keyboards.basic_keyboards as base_keyboard

router = Router()

@router.message(and_f(or_f(st.ClientState.VALUTE, st.ClientState.CALC), F.text == 'Показать курс на конкретную дату'))
async def handle_curs_date_response(message, state):
    await state.set_state(st.ClientState.DATE)
    await message.answer(text='Пожалуйста, введите требуемую дату в следующем формате: дд.мм.гггг', reply_markup=base_keyboard.curs_choice_result_kb(st.ClientState.DATE))


@router.message(st.ClientState.DATE,)
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
            await message.answer("Нету данных ЦБ РФ на данную дату, возможно на тот момент ЦБ РФ ещё не указывал курс для данной валюты. Попробуйте указать более позднюю дату.")
    else:
        await message.answer("Извините, формат некорректен. Введите дату в формате дд.мм.гггг.\nНапример 05.12.2006")