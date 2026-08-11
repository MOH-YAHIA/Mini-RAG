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