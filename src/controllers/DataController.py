from .BaseController import BaseController
from fastapi import APIRouter, FastAPI, Depends, UploadFile 
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        # Additional initialization for DataController can be added here
        self.size_scale = 1024 * 1024
    
    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True , ResponseSignal.FILE_VALIDATED_SUCCESS.value 
    
    def generate_unique_filepath(self, orig_file_name: str, project_id: str) -> str:
        """
        Generates a unique filename for the uploaded file.
        """
        random_filename = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(orig_file_name)

        new_file_path = os.path.join(
            project_path,
            random_filename + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_filename = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_filename + "_" + cleaned_file_name
            )
        
        return new_file_path, random_filename + "_" + cleaned_file_name
    
    def get_clean_file_name(self, file_name: str) -> str:
        # remove special characters, except undersocre and . 
        cleaned_file_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file_name.strip())

        # replace spaces with underscores
        clean_name = cleaned_file_name.replace(" ", "_")

        return clean_name