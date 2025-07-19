from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums 
from controllers.BaseController import BaseController
class VectorDBProviderFactory:

    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider:str) :
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_NAME)
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        

        return None