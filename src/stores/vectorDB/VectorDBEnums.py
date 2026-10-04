from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"

class DistanceMethodEnums(Enum):
    COSINE = "COSINE"
    DOT = "DOT"

class PgVectorEnums(Enum):
    TABLE_PREFIX = "pgvector_"
    DISTANCE_METHOD_COSINE = "vector_cosine_ops"
    DISTANCE_METHOD_DOT = "vector_dot_ops"
    INDEX_TYPE_IVFFLAT = "ivfflat"
    INDEX_TYPE_HNSW = "hnsw"
class PgVectorTableSchemeEnums(Enum):
    ID = 'id'
    TEXT = 'text'
    VECTOR = 'vector'
    CHUNK_ID = 'chunk_id'
    METADATA = 'metadata'