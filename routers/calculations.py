from aiogram import Router, F
from aiogram.filters import and_f, or_f
import keyboards.basic_keyboards as base_keyboard
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
async def handle_curs_calc_ye(message, state):
    await state.set_state(st.ClientState.VAL_TO_RUB)
    await message.answer(text="Введите количество валюты", reply_markup=base_keyboard.curs_calculator_kb(st.ClientState.VAL_TO_RUB))


@router.message(and_f(or_f(st.ClientState.CALC, st.ClientState.VAL_TO_RUB), F.text == 'Переведи рубли в валюту'))
async def handle_curs_calc_ru(message, state):
    await state.set_state(st.ClientState.RUB_TO_VAL)
    await message.answer(text="Введите количество рублей", reply_markup=base_keyboard.curs_calculator_kb(st.ClientState.RUB_TO_VAL))


@router.message(or_f(st.ClientState.VAL_TO_RUB, st.ClientState.RUB_TO_VAL))
async def handle_curs_calc_fin(message, state):
    current_state = await state.get_state()
    valute_data = await state.get_data()
    value_cb = valute_data['VALUE_CB']
    symbol = valute_data['SYMBOL']
    text_without_commas = message.text.replace(',', '.')
    if text_without_commas.isdigit() or text_without_commas.replace('.', '', 1).isdigit():
        if current_state == st.ClientState.VAL_TO_RUB:
            value = float(text_without_commas) * value_cb
            main_symbol = symbol
            second_symbol = '₽'
        else:
            value = float(text_without_commas) / value_cb
            main_symbol = '₽'
            second_symbol = symbol
    else:
        value = "Введите пожалуйста только целое или дробное число."
    await message.answer(text=f"{text_without_commas}{main_symbol} это {round(value,2)}{second_symbol}", reply_markup=base_keyboard.curs_calculator_kb(current_state))
