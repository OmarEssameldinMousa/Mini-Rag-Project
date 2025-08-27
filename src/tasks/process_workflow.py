from celery_app import celery_app, get_setup_utils
from helpers.config import get_settings
import asyncio
from celery import chain
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.ResponseEnums import ResponseSignal
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers import NLPController, ProcessController
import logging
from tasks.file_processing import process_project_files  
from tasks.data_indexing import _index_data_content

logger = logging.getLogger(__name__)

@celery_app.task(bind=True,name="tasks.process_workflow.push_after_process_task", 
                 autoretry_for=(Exception,), 
                 retry_kwargs={"max_retries": 3, "countdown": 60})

def push_after_process_task(self, prev_task_result):
    project_id = prev_task_result.get("project_id")
    do_reset = prev_task_result.get("do_reset")
    task_results = asyncio.run(_index_data_content(project_id=project_id, do_reset=do_reset))
    return {
        "project_id": project_id,
        "do_reset": do_reset,
        "task_results": task_results
    }


@celery_app.task(bind=True,name="tasks.process_workflow.process_and_push_workflow", 
                 autoretry_for=(Exception,), 
                 retry_kwargs={"max_retries": 3, "countdown": 60})
def process_and_push_workflow(self, project_id: int, file_id: int, chunk_size: int, overlap_size: int, do_reset: bool):

    workflow = chain(
        process_project_files.s(project_id, file_id, chunk_size, overlap_size, do_reset),
        push_after_process_task.s()
    )

    result = workflow.apply_async()

    return {
        "signal": "WORKFLOW_STARTED",
        "workflow_id": result.id,
        "tasks": ["tasks.file_processing.process_project_files", "tasks.data_indexing.index_data_content"]
    }