import requests
import variables.constans as const
from curs_data import cb_date, month_formatter

def get_curs_all():
    try:
        response_cb_all = requests.get(const.URL_CB)
    except Exception:
        currency_all_text = "Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже"
    currency_data_cb_all = ""
    currency_all_text = ""

    if response_cb_all and response_cb_all.status_code == 200:
        data_cb_all = response_cb_all.json()
        currency_data_cb_all = data_cb_all.get("Valute", {})
        date_cb = cb_date(data_cb_all)
        currency_all_text = currency_all_text + f"Курс ЦБ актуален на {month_formatter(date_cb)}\n"
    else:
        currency_all_text = 'Не удалось получить данные по курсу ЦБ, попробуйте сделать запрос позже'

    for iterator in const.CURS_DATA:
        smile_flag = const.CURS_DATA[iterator]['Emoji']
        name = const.CURS_DATA[iterator]['Name']
        try:
            nominal = currency_data_cb_all[iterator]["Nominal"]
            value_cb = currency_data_cb_all[iterator]['Value'] / nominal
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

                
        currency_all = f"{smile_flag} {name}\nЦБ {round(value_cb,2)}({sign}{round(value_cb_diff,5)}{smile})"
        currency_result = f"{currency_all_text}\n{currency_all}"
    
    return currency_result