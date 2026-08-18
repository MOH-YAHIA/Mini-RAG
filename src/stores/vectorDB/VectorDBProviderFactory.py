from .VectorDBEnums import VectorDBEnums
from .providers import QdrantProvider
from helpers.config import Settings
from controllers.BaseController import BaseController

class VectorDBProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
        self.base_controller = BaseController()

    def get_provider(self):
        if self.config.VECTOR_DB_PROVIDER == VectorDBEnums.QDRANT.value:
            client =  QdrantProvider(
                db_path = self.config.VECTOR_DB_PATH
            )
        return client