import math

from .DatabaseModel import DatabaseModel
from .enums.DatabaseEnums import DatabaseEnums
from .db_schemes.chunk import Chunk
from pymongo import InsertOne

class ChunkModel(DatabaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)

        self.collection = self.db_client[DatabaseEnums.CHUNKS.value]

    @classmethod
    async def create_instance(cls,db_client):
        await cls.create_index(db_client)
        model = cls(db_client)
        return model

    @staticmethod
    async def create_index(db_client):
        collection = db_client[DatabaseEnums.CHUNKS.value]
        for index in Chunk.get_indexes():
            await collection.create_index(
                index["keys"],
                name=index["name"],
                **index["options"]
            )
                  
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

    async def get_chunks_by_project_id(self, project_id, batch_size=100):
        # count total number of documents
        documents_count = await self.collection.count_documents({})

        # calculate total number of pages
        total_batches = math.ceil( documents_count / batch_size)
        chunks = []
        for i in range(0, total_batches, batch_size):
            batch = await self.collection.find({"chunk_project_id": project_id}).skip(i).limit(batch_size).to_list(length=None)   
            for document in batch:
                chunks.append(
                    Chunk(**document)
                )

        return chunks

    async def get_chunks_by_asset_id(self, project_id, batch_size=100):
        # count total number of documents
        documents_count = await self.collection.count_documents({})

        # calculate total number of pages
        total_batches = math.ceil( documents_count / batch_size)
        chunks = []
        for i in range(0, total_batches, batch_size):
            batch = await self.collection.find({"chunk_asset_id": project_id}).skip(i).limit(batch_size).to_list(length=None)   
            for document in batch:
                chunks.append(
                    Chunk(**document)
                )

        return chunks