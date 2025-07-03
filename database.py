from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, DateTime, select, func
from datetime import datetime
import os
from typing import Optional


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


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = async_sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("База данных инициализирована")
    
    async def add_user(self, user_id: int, username: Optional[str] = None) -> bool:
        """Добавление пользователя в базу данных"""
        try:
            async with self.async_session() as session:
                # Проверяем, существует ли пользователь
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"Пользователь {user_id} уже существует в базе")
                    return True

                # Создаем нового пользователя
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
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя из базы данных"""
        try:
            async with self.async_session() as session:
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            print(f"Ошибка при получении пользователя из БД: {e}")
            return None
    
    async def get_all_users(self) -> list[User]:
        """Получение всех пользователей из базы данных"""
        try:
            async with self.async_session() as session:
                stmt = select(User)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Ошибка при получении всех пользователей из БД: {e}")
            return []
    
    async def update_user_username(self, user_id: int, new_username: str) -> bool:
        """Обновление username пользователя"""
        try:
            async with self.async_session() as session:
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    user.username = new_username
                    await session.commit()
                    print(f"Username пользователя {user_id} обновлен")
                    return True
                else:
                    print(f"Пользователь {user_id} не найден")
                    return False
                    
        except Exception as e:
            print(f"Ошибка при обновлении username пользователя: {e}")
            return False
    
    async def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя из базы данных"""
        try:
            async with self.async_session() as session:
                stmt = select(User).where(User.user_id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    await session.delete(user)
                    await session.commit()
                    print(f"Пользователь {user_id} удален из базы")
                    return True
                else:
                    print(f"Пользователь {user_id} не найден")
                    return False
                    
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {e}")
            return False
    
    async def get_users_count(self) -> int:
        """Получение количества пользователей"""
        try:
            async with self.async_session() as session:
                stmt = select(func.count(User.id))
                result = await session.execute(stmt)
                return result.scalar() or 0
        except Exception as e:
            print(f"Ошибка при подсчете пользователей: {e}")
            return 0
    
    async def close(self):
        """Закрытие соединения с базой данных"""
        await self.engine.dispose()
        print("Соединение с базой данных закрыто")