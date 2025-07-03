from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List
import asyncio
import os
from dotenv import load_dotenv
import aiohttp
from database import DatabaseManager
from Cases import get_random_gift

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_API_URL = str(os.getenv("BOT_API_URL"))
if not BOT_API_URL:
    raise ValueError("BOT_API_URL не найден в .env файле")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env файле")

db_manager = DatabaseManager(DATABASE_URL)

@app.get("/open_case")
async def open_case():
    gift = get_random_gift()
    print(f"Выпал подарок за {gift.cost} руб.")
    return {"gift": gift.cost}