from enum import Enum


class DataBaseEnum(str, Enum):
    COLLECTION_PROJECT_NAME = "projects"
    COLLECTION_CHUNK_NAME = "documents"
    COLLECTION_ASSET_NAME = "assets"