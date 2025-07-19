from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    FAISS = "FAISS"
    MILVUS = "MILVUS"       


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"