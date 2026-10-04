from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from models.db_schemes import AlchemyBase, AlchemyProject, AlchemyAsset, AlchemyChunk
from helpers.config import get_settings
class DatabaseManager:
    def __init__(self,database_url: str) -> None:

        self.engine = create_async_engine(
                database_url, # see the database location, the driver to use.
                echo=False, # if you want to see the SQL statements
            )
        self.session_manager = async_sessionmaker(
            self.engine,
            class_=AsyncSession, # the type of session to create
            expire_on_commit=False, # disable expire on commit. 
        ) 

    async def create_tables(self) -> None:
        async with self.engine.begin() as connection:
            # Enable pgvector extension
            await connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )
            # Enable pg_trgm extension
            await connection.execute(
                text("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            )
            await connection.run_sync(
                AlchemyBase.metadata.create_all # create all tables witch inherit from AlchemyBase if not exist
            )

        return None

    async def close_database_engine(self) -> None:
        await self.engine.dispose()

async def get_db():
    db_url = get_settings().DATABASE_URL
    database_manager = DatabaseManager(db_url)
    async with database_manager.session_manager() as session:
        yield session

    await database_manager.close_database_engine()