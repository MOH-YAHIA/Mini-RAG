from qdrant_client import models, QdrantClient
from .ProviderInterface import ProviderInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List


class QdrantProvider(ProviderInterface):

    def __init__(self, db_path: str ):

        self.client = None
        self.db_path = db_path


        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(
            collection_name=collection_name
        )

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(
            collection_name=collection_name
        )

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(
                collection_name=collection_name
            )

    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        distance_method: str,
        do_reset: bool = False,
    ):
        if do_reset:
            self.delete_collection(collection_name=collection_name)

        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            distance_method = models.Distance.DOT

        if not self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=distance_method,
                ),
            )

            return True

        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        point_id: str = None,
    ):
        if not self.is_collection_existed(collection_name):
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
                        id=point_id,
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

    def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        point_ids: list = None,
        batch_size: int = 50,
    ):
        if not self.is_collection_existed(collection_name):
            self.logger.error(
                f"Can not insert points to non-existed collection: "
                f"{collection_name}"
            )
            return False

        if metadata is None:
            metadata = [None] * len(texts)

        if point_ids is None:
            point_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_ids = point_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_ids[x],
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
            except Exception as e:
                self.logger.error(
                    f"Error while inserting batch: {e}"
                )
                return False

        return True

    def search_by_vector(
        self,
        collection_name: str,
        vector: list,
        limit: int = 5,
    ):
        return self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points