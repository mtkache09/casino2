from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio

bot = Bot(token="7993685695:AAHYUIY9YaI0oDK4OZKg0LpQgr65CWrpcBg")
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Mini App",
            web_app=WebAppInfo(url="https://mtkache09.github.io/untitled3/")
        )]
    ])
    await message.answer("Жми кнопку, чтобы открыть Casino App👇", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
