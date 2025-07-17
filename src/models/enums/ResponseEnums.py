from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "File_validated_successfully"
    FILE_TYPE_NOT_SUPPORTED = "File_type_not_supported"
    FILE_SIZE_EXCEEDED = "File_size_exceeded"
    FILE_UPLOAD_FAILED = "File_upload_failed"
    FILE_UPLOAD_SUCCESS = "File_upload_successful"
    PROCESSING_FAILED = "Processing_failed"
    PROCESSING_SUCCESS = "Processing_successful"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR= "no_file_found_with_given_id"