from aiogram.fsm.state import State, StatesGroup

class ClientState(StatesGroup):
    VALUTE = State()
    MAIN_MENU = State()
    DATE = State()
    CALC = State()
    RUB_TO_VAL = State()
    VAL_TO_RUB = State()