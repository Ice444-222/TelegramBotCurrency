from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, and_f, or_f
import keyboards.basic_keyboards as base_keyboard
from aiogram.fsm.state import State, StatesGroup
import variables.states as st

router = Router()




@router.message(and_f(or_f(st.ClientState.VALUTE, st.ClientState.DATE), F.text == 'Калькулятор'))
async def handle_curs_date_response(message, state):
    await state.set_state(st.ClientState.CALC)
    await message.answer(text="Считаю", reply_markup=base_keyboard.curs_calculator_kb(st.ClientState.CALC))

@router.message(and_f(or_f(st.ClientState.CALC, st.ClientState.VAL_TO_RUB, st.ClientState.RUB_TO_VAL), F.text == 'Прибавь 1% к курсу ЦБ!'))
async def handle_curs_date_response(message, state):
    await state.set_state(st.ClientState.CALC)
    valute_data = await state.get_data()
    value_cb = valute_data['VALUE_CB']
    value_percent = value_cb*101/100
    await message.answer(text=f"Готово! {round(value_cb,4)} => {round(value_percent,4)}", reply_markup=base_keyboard.curs_calculator_kb(st.ClientState.CALC))


@router.message(and_f(or_f(st.ClientState.CALC, st.ClientState.RUB_TO_VAL), F.text == 'Переведи валюту в рубли'))
async def handle_curs_date_response(message, state):
    await state.set_state(st.ClientState.VAL_TO_RUB)
    await message.answer(text="Введите количество валюты", reply_markup=base_keyboard.curs_calculator_kb(st.ClientState.VAL_TO_RUB))


@router.message(and_f(or_f(st.ClientState.CALC, st.ClientState.VAL_TO_RUB), F.text == 'Переведи рубли в валюту'))
async def handle_curs_date_response(message, state):
    await state.set_state(st.ClientState.RUB_TO_VAL)
    await message.answer(text="Введите количество рублей", reply_markup=base_keyboard.curs_calculator_kb(st.ClientState.RUB_TO_VAL))