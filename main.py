from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.filters import Command
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, DateTime, select
from sqlalchemy.exc import IntegrityError

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

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, username='{self.username}')>"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована")

async def add_user_to_db(user_id: int, username: str | None = None) -> bool:
    """Добавление пользователя в базу данных"""
    try:
        async with async_session() as session:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"Пользователь {user_id} уже существует в базе")
                return True

            new_user = User(
                user_id=user_id,
                username=username,
                registration_date=datetime.now()
            )
            
            session.add(new_user)
            await session.commit()
            print(f"Пользователь {user_id} успешно добавлен в базу")
            return True
            
    except Exception as e:
        print(f"Ошибка при добавлении пользователя в БД: {e}")
        return False

async def get_user_from_db(user_id: int) -> User | None:
    """Получение пользователя из базы данных"""
    try:
        async with async_session() as session:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    except Exception as e:
        print(f"Ошибка при получении пользователя из БД: {e}")
        return None

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
    
    success = await add_user_to_db(user_id, username)
    
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
        
    user = await get_user_from_db(message.from_user.id)
    
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
    await init_db()
    
    print("Запуск бота...")
    print(f"Web App URL: {WEB_APP_URL}")
    
    try:
        await dp.start_polling(bot)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
