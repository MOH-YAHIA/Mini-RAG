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
    ChunksIndexedSuccess = 'chunks_indexed_success'
    ChunksIndexedFaild = 'chunks_indexed_failed'

    VECTORDB_SEARCH_FAILD = 'vector_db_search_failed'
    VECTORDB_SEARCH_SUCCESS = 'vector_db_search_success'

    CollectionNotFound = 'collection_not_found'
    CollectionInfoSuccess = 'collection_info_success'