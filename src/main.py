from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from database.database_manager import DatabaseManager
from motor.motor_asyncio import AsyncIOMotorClient

from routes import documents_router, health_router, rag_router
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.vectorDB import VectorDBProviderFactory

import logging

logging.basicConfig(
    level=logging.INFO,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    
    database_manager = DatabaseManager(
        settings.DATABASE_URL
    )

    # Create database tables if not exist
    await database_manager.create_tables()

    # Create session manager
    session_manager = database_manager.get_async_session_manager()

    # Open database session
    async with session_manager() as session:
        app.db_client = session


    app.llm_provider = LLMProviderFactory(settings).get_provider()
    app.vector_db_provider = VectorDBProviderFactory(settings).get_provider()
    app.vector_db_provider.connect()

    yield

    # Shutdown
    await database_manager.close_database_engine()
    app.vector_db_provider.disconnect()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(rag_router)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

  # uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload