from aiogram import types
from variables.constans import CURS_DATA
from aiogram.fsm.state import State, StatesGroup

class ClientState(StatesGroup):
    VALUTE = State()
    MAIN_MENU = State()
    DATE = State()
    CALC = State()
    RUB_TO_VAL = State()
    VAL_TO_RUB = State()

def get_on_start_kb():
    button_start_all = types.KeyboardButton(text='Показать все курсы валют!')
    button_start_choice = types.KeyboardButton(text='Выбрать интересующий курс')
    buttons_row_first = [button_start_all, button_start_choice]
    keyboard = types.ReplyKeyboardMarkup(keyboard=[buttons_row_first], resize_keyboard=True)
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
    button_choice_menu = types.KeyboardButton(text="В главное меню")
    buttons.append([button_choice_menu])
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
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
    button_choice_menu = types.KeyboardButton(text="В главное меню")
    buttons.append([button_choice_menu])
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

def curs_choice_result_kb(current_state):
    button_choice_result_back = types.KeyboardButton(text='Назад к выбору валюты')
    button_choice_result_menu = types.KeyboardButton(text='В главное меню')
    button_choice_result_calc = types.KeyboardButton(text='Калькулятор')
    buttons_row_first = [button_choice_result_back, button_choice_result_menu]
    buttons_row_second = [button_choice_result_calc]
    if current_state == ClientState.VALUTE:
        button_choice_result_date = types.KeyboardButton(text='Показать курс на конкретную дату')
        buttons_row_second.append(button_choice_result_date)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[buttons_row_first, buttons_row_second], resize_keyboard=True)
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