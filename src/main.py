from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

from routes import base, data
from helpers.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    env_vars = get_settings()

    app.mongodb_conn = AsyncIOMotorClient(env_vars.MONGODB_URL) # Create/configure the client. No DB I/O is awaited here. 
    app.mongodb_client = app.mongodb_conn[env_vars.MONGODB_DATABASE]

    yield

    # Shutdown
    app.mongodb_conn.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(base.router)
    app.include_router(data.router)

    return app


def main():
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()