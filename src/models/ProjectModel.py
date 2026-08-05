from .DatabaseModel import DatabaseModel
from .enums.DatabaseEnums import DatabaseEnums
from .db_schema import Project


class ProjectModel(DatabaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)

        self.collection = self.db_client[DatabaseEnums.PROJECTS.value]


    async def insert_project(self, project_id):
        project = Project(project_id=project_id)
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_none=True))
        project.id = result.inserted_id

        return project

    async def find_project(self,project_id):
        '''
        Retrieve a project by its ID.
        insert the project if it does not exist.
        '''
        record = await self.collection.find_one({"project_id": project_id})
        if record is None:
            project = await self.insert_project(project_id)
        else:
            project = Project(**record)

        return project



    
