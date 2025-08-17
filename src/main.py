from fastapi import FastAPI
from routes import base, data, nlp
# from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templatess.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    #initialize db connection
    # app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)

    app.state.db_client = sessionmaker(
        app.db_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    # Initialize LLM and VectorDB providers
    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.state.db_client)

    # Generation client setup    
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client setup    
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )
    # VectorDB client setup
    app.vectordb_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )

    yield
    # app.state.mongo_conn.close()
    await app.db_engine.dispose()
    await app.vectordb_client.disconnect()

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
