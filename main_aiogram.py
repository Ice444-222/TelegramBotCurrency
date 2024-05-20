import asyncio
import configs
import re
import locale
from aiogram import Bot, Dispatcher
import logging
from aiogram.fsm.storage.memory import MemoryStorage
from routers import router as main_router
import keyboards.basic_keyboards as base_keyboard
import variables.constans as const
import variables.states as st
import functions.data_parse as parse

locale.setlocale(locale.LC_TIME, 'ru_RU')
storage = MemoryStorage()
bot = Bot(token=configs.TOKEN)
dp = Dispatcher()
dp.include_router(main_router)


@dp.message(
    lambda message: any(
        re.search(
            r'\b{}\b'.format(re.escape(message.text.casefold())), data['Name'].casefold()
        ) for data in const.CURS_DATA.values()
    )
)
@dp.message(
    lambda message: any(
        f"{data['Emoji']} {data['Name']}" in message.text for data in const.CURS_DATA.values()
    )
)
async def handle_curs_prompt(message, state):
    await message.answer(
        text=await parse.handle_currency_choice(message, state),
        reply_markup=base_keyboard.curs_choice_result_kb(st.ClientState.VALUTE)
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

asyncio.run(main())
