import hashlib
import json 
from datetime import datetime, timezone, timedelta
from sqlalchemy import delete
from requests import session
from sqlalchemy import select 
from models.db_schemes.minirag.schemes.celery_task_execution import CeleryTaskExecution

class IdempotencyManager:
    def __init__(self, db_client, db_engine):
        self.db_client = db_client
        self.db_engine = db_engine

    def create_args_hash(self, task_name: str, task_args: dict):
        combined_data = {
            **task_args,
            "task_name": task_name
        }
        json_string = json.dumps(combined_data, sort_keys=True, default=str)
        return hashlib.sha256(json_string.encode()).hexdigest()
    
    async def create_task_record(self, task_name:str, task_args: dict, celery_task_id: str = None) -> CeleryTaskExecution:

        args_hash = self.create_args_hash(task_name, task_args)

        task_record = CeleryTaskExecution(
            task_name = task_name,
            task_args_hash = args_hash,
            task_args = task_args,
            celery_task_id = celery_task_id,
            status = "PENDING",
            started_at = datetime.utcnow(),
        )
        session = self.db_client()
        try:
            session.add(task_record)
            await session.commit()
            await session.refresh(task_record)
            return task_record
        finally:
            await session.close()

    async def update_task_status(self, execution_id: int, status: str, result: dict = None):

        session = self.db_client()
        try:
            task_record = await session.get(CeleryTaskExecution, execution_id)
            if task_record:
                task_record.status = status
                if result is not None:
                    task_record.result = result
                if status in ["SUCCESS", "FAILURE"]:
                    task_record.completed_at = datetime.utcnow()
                await session.commit()
        finally:
            await session.close()

    async def get_existing_task(self, task_name: str, task_args: dict,  celery_task_id: str):
        args_hash = self.create_args_hash(task_name, task_args)

        session = self.db_client()
        try:
            stmt = select(CeleryTaskExecution).where(
                CeleryTaskExecution.celery_task_id == celery_task_id,
                CeleryTaskExecution.task_name == task_name,
                CeleryTaskExecution.task_args_hash == args_hash
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        finally:
            await session.close()

    async def should_execute_task(self,task_name: str, task_args: dict,
                                  celery_task_id: str,  task_time_limit: int = 600) -> tuple[bool, CeleryTaskExecution ]:

        existing_task = await self.get_existing_task(task_name, task_args, celery_task_id)

        if not existing_task:
            return True, None
        
        if existing_task.status == "SUCCESS":
            return False, existing_task
        

        if existing_task.status in ["PENDING", "RETRY", "STARTED"]:
            if existing_task.started_at:
                elapsed_time = (datetime.utcnow() - existing_task.started_at).total_seconds()
                time_gap = 60
                if elapsed_time > (task_time_limit + time_gap):
                    return True, existing_task
            return False, existing_task

        return True, existing_task
    
    async def cleanup_old_tasks(self, time_retention: int = 86400) -> int:
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_retention)
        
        session = self.db_client()
        try:
            stmt = delete(CeleryTaskExecution).where(
                CeleryTaskExecution.created_at < cutoff_time
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        finally:
            await session.close()