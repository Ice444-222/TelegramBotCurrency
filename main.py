from telegram import Bot
import requests
import xml.etree.ElementTree as ET
from telegram.ext import Updater, CommandHandler, MessageHandler
import configs
from telegram import ReplyKeyboardMarkup


bot = Bot(token=configs.TOKEN)
updater = Updater(token=configs.TOKEN)
chat_id = configs.CHAT_ID
valute_id = "GBP"
URL_CB = "https://www.cbr-xml-daily.ru/daily_json.js"

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

def wake_up(update, context):
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/curs']])
    context.bot.send_message(
        chat_id=chat_id,
        text='Спасибо, что вы включили меня, {}!'.format(name),
        reply_markup=button  
    )

def show_exchange_rate(update, context):
    text = get_curs(valute_id)
    if text:
        context.bot.send_message(chat_id, text)
    else:
        context.bot.send_message(chat_id, "Failed to fetch exchange rate information.")

updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(CommandHandler('curs', show_exchange_rate))
updater.start_polling()
updater.idle()
