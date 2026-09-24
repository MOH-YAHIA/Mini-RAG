from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_schemes import Chunk, AlchemyChunk


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_alchemy(chunk: Chunk) -> AlchemyChunk:
        """
        Convert Pydantic Chunk -> SQLAlchemy AlchemyChunk.
        """
        return AlchemyChunk(
            id=chunk.id,
            chunk_text=chunk.chunk_text,
            chunk_metadata=chunk.chunk_metadata,
            chunk_order=chunk.chunk_order,
            chunk_project_id=chunk.chunk_project_id,
            chunk_asset_id=chunk.chunk_asset_id,
        )

    @staticmethod
    def _to_pydantic(chunk: AlchemyChunk) -> Chunk:
        """
        Convert SQLAlchemy AlchemyChunk -> Pydantic Chunk.
        """
        return Chunk.model_validate(chunk)

    async def insert_chunk(self, chunk: Chunk) -> Chunk:
        """
        Insert one chunk.
        """
        db_chunk = self._to_alchemy(chunk)

        self.session.add(db_chunk)

        await self.session.commit()

        return self._to_pydantic(db_chunk)

    async def find_chunk(self, chunk_id: UUID) -> Chunk | None:
        """
        Retrieve a chunk by its ID.

        Returns None if the chunk does not exist.
        """
        stmt = select(AlchemyChunk).where(
            AlchemyChunk.id == chunk_id
        )

        result = await self.session.execute(stmt)

        db_chunk = result.scalar_one_or_none()

        if db_chunk is None:
            return None

        return self._to_pydantic(db_chunk)

    async def insert_chunks(
        self,
        chunks: list[Chunk],
        batch_size: int = 100,
    ) -> int:
        """
        Insert multiple chunks in batches.

        Returns the number of chunks inserted.
        """
        if not chunks:
            return 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            db_chunks = [
                self._to_alchemy(chunk)
                for chunk in batch
            ]

            self.session.add_all(db_chunks)

            await self.session.commit()

        return len(chunks)

    async def delete_chunks_by_project_id(
        self,
        project_id: UUID,
    ) -> int:
        """
        Delete all chunks belonging to a project.

        Returns the number of deleted chunks.
        """
        stmt = delete(AlchemyChunk).where(
            AlchemyChunk.chunk_project_id == project_id
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def get_chunks_by_project_id(
        self,
        project_id: UUID,
        batch_size: int = 100,
    ) -> list[Chunk]:
        """
        Retrieve all chunks belonging to a project.

        Results are returned as Pydantic Chunk objects.
        """
        stmt = (
            select(AlchemyChunk)
            .where(
                AlchemyChunk.chunk_project_id == project_id
            )
            .order_by(AlchemyChunk.chunk_order)
        )

        result = await self.session.execute(stmt)

        db_chunks = result.scalars().all()

        return [
            self._to_pydantic(db_chunk)
            for db_chunk in db_chunks
        ]

    async def get_chunks_by_asset_id(
        self,
        asset_id: UUID,
        batch_size: int = 100,
    ) -> list[Chunk]:
        """
        Retrieve all chunks belonging to an asset.

        Results are returned as Pydantic Chunk objects.
        """
        stmt = (
            select(AlchemyChunk)
            .where(
                AlchemyChunk.chunk_asset_id == asset_id
            )
            .order_by(AlchemyChunk.chunk_order)
        )

        result = await self.session.execute(stmt)

        db_chunks = result.scalars().all()

        return [
            self._to_pydantic(db_chunk)
            for db_chunk in db_chunks
        ]