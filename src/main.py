from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    yield
    app.state.mongo_conn.close()

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
