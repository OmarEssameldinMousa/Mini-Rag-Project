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
    PROJECT_NOT_FOUND_ERROR = "project_not_found"
    INSERT_INTO_VECTORDB_ERROR = "insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    VECTORDB_SEARCH_SUCCESS = "vectordb_search_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCESS = "rag_answer_success"
    DATA_PUSH_TASK_READY = "data_push_task_ready"
    PROCESS_AND_PUSH_WORKFLOW_READY = "process_and_push_workflow_ready"
    