from .VectorDBEnums import VectorDBEnums
from .providers import QdrantProvider, PgvectorProvider
from helpers.config import Settings

class VectorDBProviderFactory:
    def __init__(self, config: Settings):
        self.config = config

    async def get_provider(self):
        if self.config.VECTOR_DB_PROVIDER == VectorDBEnums.QDRANT.value:
            client =  QdrantProvider(
                db_url = self.config.VECTOR_DB_PATH,
                default_vector_size = self.config.DEFAULT_VECTOR_SIZE,
                distance_method = self.config.DISTANCE_METHOD,
                index_threshold = self.config.INDEX_THRESHOLD
            )
            return client

        if self.config.VECTOR_DB_PROVIDER == VectorDBEnums.PGVECTOR.value:
            client =  PgvectorProvider(
                db_url = self.config.VECTOR_DB_PATH,
                default_vector_size = self.config.DEFAULT_VECTOR_SIZE,
                distance_method = self.config.DISTANCE_METHOD,
                index_threshold = self.config.INDEX_THRESHOLD
            )
            await client.connect()
            return client