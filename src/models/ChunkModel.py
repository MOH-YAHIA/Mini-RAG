from .DatabaseModel import DatabaseModel
from .enums.DatabaseEnums import DatabaseEnums
from .db_schema.chunk import Chunk
from pymongo import InsertOne

class ChunkModel(DatabaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)

        self.collection = self.db_client[DatabaseEnums.CHUNKS.value]


    async def insert_chunk(self, chunk):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_none=True))
        chunk.id = result.inserted_id

        return chunk

    async def find_chunk(self, chunk_id):
        '''
        Retrieve a chunk by its ID.
        return none if it does not exist.
        '''
        record = await self.collection.find_one({"id": chunk_id})
        if record is None:
            return None
        
        chunk = Chunk(**record)

        return chunk

    async def insert_chunks(self, chunks,batch_size=100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operations = [InsertOne(chunk.model_dump(by_alias=True, exclude_none=True)) for chunk in batch]
            await self.collection.bulk_write(operations, ordered=False)


        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
