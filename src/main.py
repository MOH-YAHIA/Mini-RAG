from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

from routes import base, data
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.vectorDB import VectorDBProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    env_vars = get_settings()

    app.mongodb_conn = AsyncIOMotorClient(env_vars.MONGODB_URL) # Create/configure the client. No DB I/O is awaited here. 
    app.mongodb_client = app.mongodb_conn[env_vars.MONGODB_DATABASE]

    app.llm_provider = LLMProviderFactory(env_vars).get_provider()
    app.vector_db_provider = VectorDBProviderFactory(env_vars).get_provider()

    print(type(app.vector_db_provider))

    yield

    # Shutdown
    app.mongodb_conn.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(base.router)
    app.include_router(data.router)
    

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

  # uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload