from aiogram import Router, F
from aiogram.filters import CommandStart, Command
import keyboards.basic_keyboards as base_keyboard
import variables.states as st
import functions.data_parse as dp

router = Router()


@router.message(CommandStart())
async def handle_start(message):
    await message.answer(text="Приветствую! Я бот для вывода актуального курса валют 🫡 ")
    await message.answer(text="Вы можете сделать запрос сразу по всем валютам чтобы увидеть актуальный курс ЦБ 👵")
    await message.answer(
        text=(
            "Также вы можете сделать запрос по конкретной "
            "валюте, посмотреть курс на конкретную дату и "
            "также увидеть курс Московской Биржы если данная валюта там торгуется. 🤑"
        ), reply_markup=base_keyboard.get_on_start_kb()
    )


@router.message(F.text == 'В главное меню')
@router.message(Command("menu"))
async def handle_menu(message, state):
    await state.set_state(st.ClientState.MAIN_MENU)
    await message.answer(text='Отправляю в главное меню...', reply_markup=base_keyboard.get_on_start_kb())

@router.message(F.text == 'Показать все курсы валют!')
@router.message(Command("curs_all"))
async def handle_curs_all(message):
    await message.answer(text = await dp.get_curs_all(), reply_markup=base_keyboard.get_on_start_kb())

@router.message(F.text == 'Выбрать интересующий курс')
@router.message(Command("curs"))
async def handle_curs_choice(message):
    await message.answer(text='Выбирайте!', reply_markup=base_keyboard.curs_choice_kb())

@router.message(F.text == 'Назад к выбору валюты')
async def handle_curs_date_response(message):
    await message.answer(text="Отправляю назад.", reply_markup=base_keyboard.curs_choice_kb())
