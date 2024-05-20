import requests
import variables.constans as const
from curs_data import cb_date, month_formatter
from aiogram import types
from aiogram.fsm.context import FSMContext
import re
from curs_data import MoexMethods
import variables.states as st


async def get_curs_all():
    try:
        response_cb_all = requests.get(const.URL_CB)
    except Exception:
        currency_all_text = (
            'Не удалось получить данные по курсу ЦБ, '
            'попробуйте сделать запрос позже'
        )
    currency_data_cb_all = ""
    currency_all_text = ""
    currency_all =""

    if response_cb_all and response_cb_all.status_code == 200:
        data_cb_all = response_cb_all.json()
        currency_data_cb_all = data_cb_all.get("Valute", {})
        date_cb = cb_date(data_cb_all)
        currency_all_text = (
            currency_all_text + f"Курс ЦБ актуален на {month_formatter(date_cb)}\n"
        )
    else:
        currency_all_text = (
            'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
        )

    for iterator in const.CURS_DATA:
        smile_flag = const.CURS_DATA[iterator]['Emoji']
        name = const.CURS_DATA[iterator]['Name']
        try:
            nominal = currency_data_cb_all[iterator]["Nominal"]
            value_cb = round(currency_data_cb_all[iterator]['Value'] / nominal, 2)
            previous_cb = currency_data_cb_all[iterator]['Previous'] / nominal
            value_cb_diff = value_cb - previous_cb
            if value_cb_diff > 0:
                smile = "💹"
                sign = "+"
            else:
                smile = "🔻"
                sign = ""
        except Exception:
            value_cb = "Не удалось загрузить данные"
        currency_all += f"{smile_flag} {name}\nЦБ {value_cb}({sign}{round(value_cb_diff,5)}{smile})\n\n"
    currency_result = f"{currency_all_text}\n{currency_all}"

    return currency_result


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
            await state.set_state(st.ClientState.VALUTE)
            await state.update_data(VALUTE=currency_choice)
            await state.update_data(SYMBOL=data['Symbol'])
            try:
                response_cb_choice = requests.get(const.URL_CB)
            except Exception:
                currency_choice_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
            if response_cb_choice and response_cb_choice.status_code == 200:
                data_cb_all = response_cb_choice.json()
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
                currency_choice_text = f"Курс Центробанка РФ:\n{round(value_cb,3)}({sign}{round(value_cb_diff,6)}{smile})\nУстановлен на:\n{month_formatter(date_cb)}\n"
            else:
                currency_choice_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'
            if data['MOEX']:
                try:
                    response_moex = MoexMethods.get_moex_repsonse(const.URL_MOEX_CHOICE, currency_choice)
                except Exception:
                    moex_message = 'Не удалось получить данные по курсу Московской биржи, попробуйте сделать запрос позже (бывает достаточно отправить ещё один запрос)'
                if response_moex and response_moex.status_code == 200:
                    response_moex = response_moex.json()
                    last_element_value = response_moex.get("securities").get("data")[-1][3]
                    value_moex = response_moex.get("securities.current").get("data")[0][3]
                    if last_element_value == value_moex:
                        value_moex_prev = (
                            response_moex.get("securities").get("data")[-2][3]
                        )
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
                    moex_message = f"Курс Московской Биржи:\n{round(value_moex,3)}({sign}{round(value_moex_diff,6)}{smile})\nПоследнее обновление:\n{time_moex} мск {month_formatter(date_moex)}"
                else:
                    moex_message = 'Не удалось получить данные по курсу Московской биржи, попробуйте сделать запрос позже (бывает достаточно отправить ещё один запрос)'
            else:
                moex_message = 'Валюта не продаётся на Московской Бирже.'
    answer = f"{moex_message}\n\n{currency_choice_text}"
    return answer
