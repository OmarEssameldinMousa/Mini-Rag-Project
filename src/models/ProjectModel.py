from .BaseDataModel import BaseDataModel
from .db_schemes import Project 
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection_name = DataBaseEnum.COLLECTION_PROJECT_NAME.value
        self.collection = self.db_client[self.collection_name]

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project._id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str) -> Project:
        
        record = await self.collection.find_one({"project_id": project_id})
        if record is None:
            # create a new project if it doesn't exist
            project = Project(project_id=project_id)
            project = await self.create_project(project)
            return project

        return Project(**record)
    
    async def get_all_projects(self, page: int = 1, page_size: int = 10) -> list[Project]:
        
        # count all the documents in the collection
        total_documents = await self.collection.count_documents({})

        total_pages = (total_documents + page_size - 1) // page_size

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        
        return projects, total_pages