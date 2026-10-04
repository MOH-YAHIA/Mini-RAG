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
   
    app.llm_provider = LLMProviderFactory(settings).get_provider()
    app.vector_db_provider = await VectorDBProviderFactory(settings).get_provider()
    await app.vector_db_provider.connect()

    yield

    # Shutdown
    await app.vector_db_provider.disconnect()

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