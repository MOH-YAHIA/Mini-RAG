from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    AssetTypeNotAllowed = "asset_type_not_allowed"
    AssetSizeExceedsLimit = "asset_size_exceeds_limit"
  
    AssetUploadFailed = "asset_upload_failed"
    NoChunksCreated = "no_chunks_created"
    AssetNotFound = "asset_not_found"

    AssetUploadSuccess = "asset_upload_success"
    AssetValidateSuccess = 'asset_validate_success'

    AssetProcessSuccess = 'asset_process_success'
    ProjectNotFound = 'project_not_found_error'
    ChunksEmbeddedSuccess = 'chunks_embedded_success'
    ChunksEmbeddedFaild = 'chunks_embedded_failed'

    VectorDBRetrieveFaild = 'vector_db_retrieve_failed'
    VectorDBRetrieveSuccess = 'vector_db_retrieve_success'

    CollectionNotFound = 'collection_not_found'
    CollectionInfoSuccess = 'collection_info_success'

    RagAnswerFaild = 'rag_answer_failed'
    RagAnswerSuccess = 'rag_answer_success'