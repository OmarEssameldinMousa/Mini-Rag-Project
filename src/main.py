from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    llm_provider_factory = LLMProviderFactory(settings)
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    yield
    app.state.mongo_conn.close()

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
