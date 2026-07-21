from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    FileTypeNotAllowed = "file_type_not_allowed"
    FileSizeExceedsLimit = "file_size_exceeds_limit"
    FileUploadSuccess = "file_upload_success"