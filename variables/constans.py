URL_CB = "https://www.cbr-xml-daily.ru/daily_json.js"
URL_CB_DATE = "https://www.cbr.ru/scripts/XML_daily.asp?date_req={}"
URL_MOEX = "https://iss.moex.com/iss/history/engines/currency/markets/index/boards/FIXI/securities.json?"
URL_MOEX_CHOICE = "https://iss.moex.com/iss/statistics/engines/futures/markets/indicativerates/securities/{}/RUB.json?from={}&till={}&iss.meta=off"
CB_ERROR = "Не удалось загрузить данные ЦБ"
CURS_DATA = {
    "GEL": {'Emoji': '🇬🇪', 'Name': 'Грузинский лари', 'Symbol': '₾', 'MOEX': False},
    "AMD": {'Emoji': '🇦🇲', 'Name': 'Армянский драм', 'Symbol': '֏', 'MOEX': False},
    "KZT": {'Emoji': '🇰🇿', 'Name': 'Казахстанский тенге', 'Symbol': '₸', 'MOEX': True},
    "CNY": {'Emoji': '🇨🇳', 'Name': 'Китайский юань', 'Symbol': '圓', 'MOEX': True},
    "INR": {'Emoji': '🇮🇳', 'Name': 'Индийская рупия', 'Symbol': '₹', 'MOEX': False},
    "USD": {'Emoji': '🇺🇸', 'Name': 'Доллар США', 'Symbol': '$', 'MOEX': True},
    "EUR": {'Emoji': '🇪🇺', 'Name': 'Евро', 'Symbol': '€', 'MOEX': True},
    "GBP": {'Emoji': '🇬🇧', 'Name': 'Британский фунт', 'Symbol': '£', 'MOEX': True},
    "TRY": {'Emoji': '🇹🇷', 'Name': 'Турецкая лира', 'Symbol': '₺', 'MOEX': True},
}
CURS_MOEX_DATA = {
    "CNY": "CNYFIX",
    "EUR": "EURFIX",
    "TRY": "TRYFIXME",
    "USD": "USDFIX",
}