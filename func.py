




def command_main():
    response_cb_all = requests.get(URL_CB)
    response_moex_all = requests.get(URL_MOEX)
    currency_data_cb_all =""
    currency_data_moex_all=""
    currency_all_text = ""
    cb_text_all = ""

    if response_cb_all.status_code == 200:
        data_cb_all = response_cb_all.json()
        currency_data_cb_all = data_cb_all.get("Valute", {})
    if response_moex_all.status_code == 200:
        data_moex_all = response_moex_all.json()
        currency_data_moex_all = data_moex_all.get("history", {}).get("data", [])

    for iterator in CURS_DATA:
        smile = CURS_DATA[iterator]['Emoji']
        name = CURS_DATA[iterator]['Name']
        try:
            nominal = currency_data_cb_all[iterator]["Nominal"]
            value_cb = round(currency_data_cb_all[iterator]['Value']/nominal, 2)
        except Exception:
            value_cb = "Не удалось загрузить данные"
        value_moex = [sublist[6] for sublist in currency_data_moex_all if sublist[1] == CURS_MOEX_DATA[iterator]]
        currency_all = f"{smile} {name} {value_cb} ЦБ {value_moex} МОЭКС \n"
        currency_all_text = currency_all_text + currency_all
    return currency_all_text


def CheckMoex(data, dict, i):
    for sublist in data:
        if sublist[1] == dict[i][0]:
            return sublist[6]
