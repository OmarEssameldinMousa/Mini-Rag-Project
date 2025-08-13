from qdrant_client import QdrantClient, models
from ..VectorDBInterface import  VectorDBInterface
from ..VectorDBEnums import VectorDBEnums, DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDB(VectorDBInterface):

    def __init__(self, db_client: str,  default_vector_size: int = 768, distance_method: str = None, index_threshold: int = 100):
        self.client = None
        self.db_client = db_client
        self.distance_method = distance_method

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        self.client = None 

    async def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self):
        return self.client.get_collections()
    
    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    async def delete_collection(self, collection_name: str) -> bool:
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False) -> bool:
        
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            self.logger.info(f"Creating new Qdrant collection: {collection_name}")
            try:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=embedding_size,
                        distance=self.distance_method
                    )
                )
                self.logger.info(f"Successfully created collection: {collection_name}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to create collection {collection_name}: {e}")
                return False
        else:
            self.logger.info(f"Collection {collection_name} already exists")
            return True
    
    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error inserting record into {collection_name}: {e}")
            return False
        return True
    
    async def insert_many(self, collection_name: str, texts: List[str], vectors: List[list], metadata: List[dict] = None, record_ids: List[str] = None, batch_size: int = 50):

        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        if metadata is None:
            metadata = [None] * len(texts)
        
        if record_ids is None:
            record_ids = list(range(len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_vectors = vectors[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]
            batch_record_ids = record_ids[i:i + batch_size]

            batch_records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch into {collection_name}: {e}")
                return False
        return True
    
    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> list:
        
        results= self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )
    
        if not results or len(results) == 0:
            return None
        return [
            RetrievedDocument(
                score=result.payload.get("score", 0.0),
                text=result.payload.get("text", "")
            )
            for result in results
        ]
    