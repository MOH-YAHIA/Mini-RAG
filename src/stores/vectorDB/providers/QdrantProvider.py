from qdrant_client import models, QdrantClient
from .ProviderInterface import ProviderInterface
from ..VectorDBEnums import DistanceMethodEnums
from ..schemes import RetrievedDocument
import logging
from typing import List
import uuid


class QdrantProvider(ProviderInterface):

    def __init__(self, db_url: str,
                default_vector_size: int = 786,
                distance_method: str = DistanceMethodEnums.COSINE.value,
                index_threshold: int=100):
        
        self.client = None
        self.db_url = db_url

        self.default_vector_size = default_vector_size

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    async def connect(self):
        try :
            self.client = QdrantClient(url=self.db_url)
            return True
        except Exception as e:
            self.logger.error(f"Error while connecting to Qdrant with Exception {e}")
            return False

    async def disconnect(self):
        self.client = None

    async def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(
            collection_name=collection_name
        )

    async def list_all_collections(self) -> List:
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str) -> dict:
        collection_info = self.client.get_collection(
            collection_name=collection_name
        )

        return {
            "collection_status": collection_info.status.value,
            "points_count": collection_info.points_count,
            "vectors_config": collection_info.config.params.vectors.model_dump()
        }

    async def delete_collection(self, collection_name: str):
        if await self.is_collection_existed(collection_name):
            return self.client.delete_collection(
                collection_name=collection_name
            )

    async def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False,
    ):
        if do_reset:
            await self.delete_collection(collection_name=collection_name)


        if not await self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method,
                ),
            )

            return True

        return False

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: int = None,
    ):
        if not await self.is_collection_existed(collection_name):
            self.logger.error(
                f"Can not insert new point to non-existed collection: "
                f"{collection_name}"
            )
            return False

        try:
            self.client.upload_points(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata,
                        },
                    )
                ],
            )
        except Exception as e:
            self.logger.error(
                f"Error while inserting point: {e}"
            )
            return False

        return True

    async def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 50,
    ):
        if not await self.is_collection_existed(collection_name):
            self.logger.error(
                f"Can not insert points to non-existed collection: "
                f"{collection_name}"
            )
            return False

        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_ids = record_ids[i:batch_end]
            self.logger.info(
                f"Inserting {len(batch_texts)} points to collection: "
                f"{collection_name}"
            )
            batch_points = [
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x],
                    },
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_points,
                )
                self.logger.info(
                    f"Inserted {len(batch_texts)} points to collection: "
                    f"{collection_name}")
                
            except Exception as e:
                self.logger.error(
                    f"Error while inserting batch: {e}"
                )
                return False

        return True

    async def search_by_vector(
        self,
        collection_name: str,
        vector: list,
        limit: int = 5,
    ):
        points =  self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points

        return [
            RetrievedDocument(
                retrieved_text=point.model_dump().get("payload").get("text"),
                score=point.model_dump().get("score"),
            )
            for point in points
        ]