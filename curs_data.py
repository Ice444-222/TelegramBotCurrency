from datetime import datetime, timedelta
import requests

CURS_DATA = {
    "GEL": {'Emoji': '🇬🇪', 'Name': 'Грузинский лари', 'Symbol': '₾', 'MOEX':False},
    "AMD": {'Emoji': '🇦🇲', 'Name': 'Армянский драм', 'Symbol': '֏', 'MOEX':False},
    "KZT": {'Emoji': '🇰🇿', 'Name': 'Казахстанский тенге', 'Symbol': '₸', 'MOEX':True},
    "CNY": {'Emoji': '🇨🇳', 'Name': 'Китайский юань', 'Symbol': '圓', 'MOEX':True},
    "INR": {'Emoji': '🇮🇳', 'Name': 'Индийская рупия', 'Symbol': '₹', 'MOEX':False},
    "USD": {'Emoji': '🇺🇸', 'Name': 'Доллар США', 'Symbol': '$', 'MOEX':True},
    "EUR": {'Emoji': '🇪🇺', 'Name': 'Евро', 'Symbol': '€', 'MOEX':True},
    "GBP": {'Emoji': '🇬🇧', 'Name': 'Британский фунт', 'Symbol': '£', 'MOEX':True},
    "TRY": {'Emoji': '🇹🇷', 'Name': 'Турецкая лира', 'Symbol': '₺', 'MOEX':True},
}

CURS_MOEX_DATA = {
    "CNY": "CNYFIX",
    "EUR": "EURFIX",
    "TRY": "TRYFIXME",
    "USD": "USDFIX",
}

CB_ERROR = "Не удалось загрузить данные ЦБ"


def month_formatter(date):
    parsed_date = datetime.strptime(date, "%Y-%m-%d")
    formatted_date = parsed_date.strftime("%d %B %Y")
    month_part = formatted_date.split(" ")[1]
    last_letter = month_part[-1]
    if last_letter == 'т':
        month_part += 'а'
    else:
        month_part = month_part[:-1] + 'я'
    modified_date = formatted_date.split(" ")[0] + " " + month_part + " " + formatted_date.split(" ")[2]
    return modified_date

def day_deleter(date,day):
    original_date = datetime.strptime(date, "%Y-%m-%d")
    new_date = original_date - timedelta(days=day)
    new_date_string = new_date.strftime("%Y-%m-%d")
    return str(new_date_string)

def check_moex(data, dict_data, i):
    for sublist in data:
        if sublist[1] == dict_data[i]:
            return sublist[6]

def cb_date(response_data):
    date_cb = (response_data.get("Date")).split("T")[0]
    return date_cb

class MoexMethods():
    @classmethod
    def get_moex_repsonse(self, url_moex, currency_choise):
        till_time = datetime.utcnow().strftime("%Y-%m-%d")
        from_time = datetime.utcnow() - timedelta(days=15)
        response_moex = (requests.get(url_moex.format(currency_choise, from_time, till_time)))
        return response_moex
     
def is_valid_date(date_string):
    try:
        # Parse the date using the specified format
        parsed_date = datetime.strptime(date_string, "%d.%m.%Y")
        min_date = datetime(1993, 10, 1)
        max_date = datetime.now() + timedelta(days=5)
        return min_date <= parsed_date <= max_date
    except ValueError:
        # The date string does not match the specified format
        return False