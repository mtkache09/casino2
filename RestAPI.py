from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List
import asyncio
import aiohttp
from database import DatabaseManager
from Cases import get_random_gift
from config import DATABASE_URL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db_manager = DatabaseManager(DATABASE_URL)

@app.get("/open_case")
async def open_case():
    gift = get_random_gift()
    print(f"Выпал подарок за {gift.cost} руб.")
    return {"gift": gift.cost}
