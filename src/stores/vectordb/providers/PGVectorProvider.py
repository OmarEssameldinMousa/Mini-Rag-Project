from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import (DistanceMethodEnums, PgVectorTableSchemeEnums, 
                             PgVectorDistanceMethodEnums, PgVectorIndexTypeEnums)

from typing import List
import logging 
from models.db_schemes import RetrievedDocument
from sqlalchemy import text as sql_text
import json

class PGVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int = 768, distance_method: str = None, index_threshold: int = 100):
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            distance_method = PgVectorDistanceMethodEnums.DOT.value
        
        self.distance_method = distance_method

        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"


    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                ))
                await session.commit() 


    async def disconnect(self):
        pass

    async def is_collection_existed(self, collection_name):
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text('SELECT * FROM pg_tables WHERE tablename = :collection_name')
                results = await session.execute(list_tbl, {'collection_name': collection_name})
                record = results.scalar_one_or_none()
        
        return record is not None
    
    async def list_all_collections(self):
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text('SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix')
                results = await session.execute(list_tbl, {'prefix': f"{self.pgvector_table_prefix}%"})
                records = results.scalars().all()
        return records


    async def get_collection_info(self, collection_name) -> dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text(f'''
                      SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                      FROM pg_tables
                      WHERE tablename = :collection_name
                ''')
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')

                table_info = await session.execute(table_info_sql, {'collection_name': collection_name})
                record_count = await session.execute(count_sql)

                table_data = table_info.fetchone()
                if not table_data:
                    return None

                return {
                    "table_info": {
                        "schemaname": table_data.schemaname,
                        "tablename": table_data.tablename,
                        "tableowner": table_data.tableowner,
                        "tablespace": table_data.tablespace,
                        "hasindexes": table_data.hasindexes
                    },
                    "record_count": record_count.scalar_one()
                }
    
    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")
                delete_sql = sql_text(f'DROP TABLE IF EXISTS {collection_name}')
                await session.execute(delete_sql)
                await session.commit()
        return True

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):

        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating collection: {collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name}('
                            f'{PgVectorTableSchemeEnums.ID.value} BIGSERIAL PRIMARY KEY,'
                            f'{PgVectorTableSchemeEnums.TEXT.value} TEXT,'
                            f'{PgVectorTableSchemeEnums.VECTOR.value} VECTOR({embedding_size}),'
                            f'{PgVectorTableSchemeEnums.METADATA.value} JSONB DEFAULT \'{{}}\','
                            f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer,'
                            f'FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_sql)
                    await session.commit()
            return True
        else:
            return False
        
    async def is_index_existed(self, collection_name):
        index_name = self.default_index_name(collection_name)  
        async with self.db_client() as session:
            async with session.begin():
                check_sql = sql_text(f"""
                                     SELECT 1 
                                     FROM pg_indexes
                                     WHERE tablename = :collection_name AND indexname = :index_name
                                """)
            result = await session.execute(check_sql, {'collection_name': collection_name, 'index_name': index_name})
            return result.scalar_one_or_none() is not None

    async def create_vector_index(self, collection_name: str,
                                        index_type: str = PgVectorIndexTypeEnums.HNSW.value):
        is_index_existed =  await self.is_index_existed(collection_name=collection_name)
        if is_index_existed: 
            return False

        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                count_result = await session.execute(count_sql)
                records_counts = count_result.scalar_one()

                if records_counts < self.index_threshold:
                    self.logger.info(f"Not enough records to create index (found: {records_counts}, required: {self.index_threshold}).")
                    return False
                
                self.logger.info(f"Creating index for collection: {collection_name}")
                
                index_name = self.default_index_name(collection_name)
                create_idx_sql = sql_text(
                    f"CREATE INDEX {index_name} ON {collection_name} USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_method})"
                )
                await session.execute(create_idx_sql)

                self.logger.info(f"END: Creating index for collection: {collection_name}")

    async def reset_vector_index(self, collection_name: str, 
                                       index_type: str = PgVectorIndexTypeEnums.HNSW.value) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                drop_idx_sql = sql_text(f"DROP INDEX IF EXISTS {index_name}")
                await session.execute(drop_idx_sql)
        return await self.create_vector_index(collection_name=collection_name, index_type=index_type)

    async def insert_one(self, collection_name, text, vector, metadata = None, record_id = None):
        
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        if not record_id:
            self.logger.error(f"Record ID is required.")
            return False

        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name}'
                                      f'({PgVectorTableSchemeEnums.TEXT.value},{PgVectorTableSchemeEnums.VECTOR.value},{PgVectorTableSchemeEnums.METADATA.value},{PgVectorTableSchemeEnums.CHUNK_ID.value})'
                                      f'VALUES (:text, :vector, :metadata, :chunk_id)'
                                )
                metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else '{}'

                await session.execute(insert_sql, {
                    'text': text,
                    'vector': "["+ ",".join([str(v) for v in vector]) + "]",
                    'metadata': metadata_json,
                    'chunk_id': record_id
                })
                await session.commit()

                await self.create_vector_index(collection_name=collection_name)

        return True

    async def insert_many(self, collection_name, texts, vectors, metadata = None, record_ids = None, batch_size = 50):

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        
        if len(vectors) != len(record_ids):
            self.logger.error(f"Vectors length {len(vectors)} does not match record IDs length {len(record_ids)}.")
            return False

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_vectors = vectors[i:i + batch_size]
                    batch_metadata = metadata[i:i + batch_size] if metadata else [None] * len(batch_texts)
                    batch_record_ids = record_ids[i:i + batch_size]

                    values = []

                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):

                        metadata_json = json.dumps(_metadata, ensure_ascii=False) if _metadata else '{}'
                        values.append(
                            {
                                'text': _text,
                                'vector': "["+ ",".join([str(v) for v in _vector]) + "]",
                                'metadata': metadata_json,
                                'chunk_id': _record_id
                            }
                        )
                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name}'
                                        f'({PgVectorTableSchemeEnums.TEXT.value}, '
                                        f'{PgVectorTableSchemeEnums.VECTOR.value}, '
                                        f'{PgVectorTableSchemeEnums.METADATA.value}, '
                                        f'{PgVectorTableSchemeEnums.CHUNK_ID.value})'
                                        f'VALUES (:text, :vector, :metadata, :chunk_id)'
                                        )
                    await session.execute(batch_insert_sql, values)

        await self.create_vector_index(collection_name=collection_name)
        
        return True
    

    async def search_by_vector(self, collection_name, vector, limit):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []

        vector = "[" + ",".join([str(v) for v in vector]) + "]"


        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(f'SELECT {PgVectorTableSchemeEnums.TEXT.value} as text, 1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) AS score'
                                      f' FROM {collection_name}'
                                      f' ORDER BY score DESC'
                                      f' LIMIT :limit'
                                      )
                result = await session.execute(search_sql, {'vector': vector, 'limit': limit})
                records = result.fetchall()

                return [
                    RetrievedDocument(
                        text=record.text,
                        score=record.score
                    )
                    for record in records
                ]