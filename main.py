from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
import os
from dotenv import load_dotenv

from database import DatabaseManager

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEB_APP_URL = os.getenv("WEB_APP_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")
if not WEB_APP_URL:
    raise ValueError("WEB_APP_URL не найден в .env файле")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env файле")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db_manager = DatabaseManager(DATABASE_URL)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await web_app_data_handler(message)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎰 Открыть Casino App",
            web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=index")
        )],
        [InlineKeyboardButton(
            text="📋 Пользовательское соглашение",
            web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=terms")
        )]
    ])
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)


@dp.message(lambda message: message.web_app_data is not None)
async def web_app_data_handler(message: types.Message):
    """Обработчик данных от Web App"""
    if not message.from_user:
        await message.answer("❌ Ошибка: данные пользователя недоступны")
        return
        
    user_id = message.from_user.id
    username = message.from_user.username or None
    
    success = await db_manager.add_user(user_id, username)
    
    if success:
        username_str = f"({username})" if username else "(без username)"
        print(f"Пользователь {user_id} {username_str} обработан")
        await message.answer("✅ Вы зарегестрированы в Casino App!")
    else:
        print(f"Ошибка при добавлении пользователя {user_id}")
        await message.answer("❌ Произошла ошибка при регистрации")


@dp.message(Command("profile"))
async def profile_handler(message: types.Message):
    """Показать информацию о пользователе"""
    if not message.from_user:
        await message.answer("❌ Ошибка: данные пользователя недоступны")
        return
        
    user = await db_manager.get_user(message.from_user.id)
    
    if user:
        username_display = f"@{user.username}" if user.username else "не указан"
        await message.answer(
            f"👤 Ваш профиль:\n"
            f"ID: {user.user_id}\n"
            f"Username: {username_display}\n"
            f"Дата регистрации: {user.registration_date.strftime('%d.%m.%Y %H:%M')}"
        )
    else:
        await message.answer("❌ Пользователь не найден в базе данных")

async def main():
    print("Инициализация базы данных...")
    await db_manager.init_db()
    
    print("Запуск бота...")
    print(f"Web App URL: {WEB_APP_URL}")
    
    try:
        await dp.start_polling(bot)
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
