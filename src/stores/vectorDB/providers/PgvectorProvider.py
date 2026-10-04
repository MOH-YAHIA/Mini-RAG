import json
from fastapi import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from .ProviderInterface import ProviderInterface
from sqlalchemy.sql import text as sql_text
from ..VectorDBEnums import DistanceMethodEnums, PgVectorEnums, PgVectorTableSchemeEnums
import logging
from ..schemes import RetrievedDocument
class PgvectorProvider(ProviderInterface):
    def __init__(self, db_url: str, 
                default_vector_size: int = 786,
                distance_method: str = DistanceMethodEnums.COSINE.value,
                index_threshold: int=100):
        
        self.db_url = db_url
        self.default_vector_size = default_vector_size
        

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = PgVectorEnums.DISTANCE_METHOD_COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = PgVectorEnums.DISTANCE_METHOD_DOT.value

        self.index_threshold = index_threshold

        self.pgvector_table_prefix = PgVectorEnums.TABLE_PREFIX.value

        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"

        self.logger = logging.getLogger(__name__)

    async def connect(self):
        engine = create_async_engine(
                        self.db_url, # see the database location, the driver to use.
                        echo=False, # if you want to see the SQL statements
                    )
        self.session_manager = async_sessionmaker(
                    engine,
                    class_=AsyncSession, # the type of session to create
                    expire_on_commit=False, # disable expire on commit. 
                ) 
        async with self.session_manager() as session:
            await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await session.commit()

    async def disconnect(self):
        pass

    async def is_collection_existed(self, collection_name: str) -> bool:
        async with self.session_manager() as session:
            table_exists_query = sql_text(f"SELECT * FROM pg_tables WHERE tablename = :collection_name")
            result = await session.execute(table_exists_query, {"collection_name": collection_name})
            return result.scalar_one_or_none()

    async def list_all_collections(self) -> list:
        async with self.session_manager() as session:
            list_tables_query = sql_text(f"SELECT tablename FROM pg_tables WHERE tablename LIKE :table_prefix")
            result = await session.execute(list_tables_query, {"table_prefix": PgVectorEnums.TABLE_PREFIX.value})
            return result.scalars().all()

    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.session_manager() as session:
            table_info_sql = sql_text(f'''
                        SELECT schemaname, tablename, tableowner, tablespace, hasindexes 
                        FROM pg_tables 
                        WHERE tablename = :collection_name
                    ''')

            count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')

            table_info = await session.execute(table_info_sql, {"collection_name": collection_name})
            record_count = await session.execute(count_sql, {"collection_name": collection_name})

            table_data = table_info.fetchone()
            if not table_data:
                return None
            
            return {
                "collection_info": {
                    "schemaname": table_data[0],
                    "tablename": table_data[1],
                    "tableowner": table_data[2],
                    "tablespace": table_data[3],
                    "hasindexes": table_data[4],
                },
                "records_count": record_count.scalar_one(),
            }

    async def delete_collection(self, collection_name: str):
        async with self.session_manager() as session:
            self.logger.info(f"Deleting collection: {collection_name}")
            await session.execute(sql_text(f"DROP TABLE IF EXISTS {collection_name}"))
            await session.commit()

    async def create_collection(self, collection_name: str,
                                      embedding_size: int,
                                      do_reset: bool = False):
        
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating collection: {collection_name}")
            create_sql = sql_text(
                f"CREATE TABLE {collection_name} ("
                f"{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,"
                f"{PgVectorTableSchemeEnums.TEXT.value} text, "
                f"{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}), "
                f"{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT '{{}}', "
                f"{PgVectorTableSchemeEnums.CHUNK_ID.value} uuid, "
                f"FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(id)"
                ")"
            )
            async with self.session_manager() as session:
                await session.execute(create_sql)
                await session.commit()

            return True
        self.logger.warning(f"Collection already exists: {collection_name}")
        return True

    async def is_index_existed(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        check_sql = sql_text(f""" 
                            SELECT 1 
                            FROM pg_indexes 
                            WHERE tablename = :collection_name
                            AND indexname = :index_name
                            """)
        async with self.session_manager() as session:
            results = await session.execute(check_sql, {"index_name": index_name, "collection_name": collection_name})
        return bool(results.scalar_one_or_none())
            
    async def create_vector_index(self, collection_name: str,
                                        index_type: str = PgVectorEnums.INDEX_TYPE_HNSW.value):
        is_index_existed = await self.is_index_existed(collection_name=collection_name)
        if is_index_existed:
            return False
        
        count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
        async with self.session_manager() as session:
            result = await session.execute(count_sql)
            await session.commit()
        records_count = result.scalar_one()

        if records_count < self.index_threshold:
            return False
        
        self.logger.info(f"START: Creating vector index for collection: {collection_name}")
        
        index_name = self.default_index_name(collection_name)
        create_idx_sql = sql_text(
                                f'CREATE INDEX {index_name} ON {collection_name} '
                                f'USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_method})'
                                )

        async with self.session_manager() as session:
            await session.execute(create_idx_sql)
            await session.commit()
        self.logger.info(f"END: Created vector index for collection: {collection_name}")

    async def reset_vector_index(self, collection_name: str, 
                                       index_type: str = PgVectorEnums.INDEX_TYPE_HNSW.value) -> bool:
        
        index_name = self.default_index_name(collection_name)
        drop_sql = sql_text(f'DROP INDEX IF EXISTS {index_name}')
        async with self.session_manager() as session:
            await session.execute(drop_sql)
            await session.commit()
        return await self.create_vector_index(collection_name=collection_name, index_type=index_type)

    
    async def insert_one(self, collection_name: str, 
                    text: str, 
                    vector: list,
                    metadata: dict = None,
                    record_id: str = None):
        
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk_id: {collection_name}")
            return False
        
     
        insert_sql = sql_text(f'INSERT INTO {collection_name} '
                            f'({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                            'VALUES (:text, :vector, :metadata, :chunk_id)'
                            )
        
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata is not None else "{}"
        async with self.session_manager() as session:
            await session.execute(insert_sql, {
                'text': text,
                'vector': "[" + ",".join([ str(v) for v in vector ]) + "]",
                'metadata': metadata_json,
                'chunk_id': record_id
            })
            await session.commit()

        await self.create_vector_index(collection_name=collection_name)
        
        return True
    

    async def insert_many(self, collection_name: str, texts: list,
                         vectors: list, metadata: list = None,
                         record_ids: list = None, batch_size: int = 50):
        
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new records to non-existed collection: {collection_name}")
            return False
        
        if not record_ids or len(vectors) != len(record_ids):
            self.logger.error(f"Invalid data items for collection: {collection_name}")
            return False
        
        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_vectors = vectors[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]
            batch_record_ids = record_ids[i:i + batch_size]

            values = []

            for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):
                
                metadata_json = json.dumps(_metadata, ensure_ascii=False) if _metadata is not None else "{}"
                values.append({
                    'text': _text,
                    'vector': "[" + ",".join([ str(v) for v in _vector ]) + "]",
                    'metadata': metadata_json,
                    'chunk_id': _record_id
                })
            
            batch_insert_sql = sql_text(f'INSERT INTO {collection_name} '
                            f'({PgVectorTableSchemeEnums.TEXT.value}, '
                            f'{PgVectorTableSchemeEnums.VECTOR.value}, '
                            f'{PgVectorTableSchemeEnums.METADATA.value}, '
                            f'{PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                            f'VALUES (:text, :vector, :metadata, :chunk_id)')
            
            async with self.session_manager() as session:
                await session.execute(batch_insert_sql, values)
                await session.commit()
        await self.create_vector_index(collection_name=collection_name)

        return True
    
    async def search_by_vector(self, collection_name: str, vector: list, limit: int):

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not search for records in a non-existed collection: {collection_name}")
            return False
        
        vector = "[" + ",".join([ str(v) for v in vector ]) + "]"
        search_sql = sql_text(f'SELECT {PgVectorTableSchemeEnums.TEXT.value} as text, 1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) as score'
                                f' FROM {collection_name}'
                                ' ORDER BY score DESC '
                                f'LIMIT {limit}'
                                )
        
        async with self.session_manager() as session:
            result = await session.execute(search_sql, {"vector": vector})
        records = result.fetchall()

        return [
            RetrievedDocument(retrieved_text=record[0], score=record[1])
            for record in records
        ]