import math

from numpy import ceil

from .DatabaseModel import DatabaseModel
from .enums.DatabaseEnums import DatabaseEnums
from .db_schema import Project


class ProjectModel(DatabaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnums.PROJECTS.value]

        # we should create indexes when the model is initialized. but as creating indexes is an async operation, we cannot do it in the constructor. so we will create a static method to create indexes and call it when the model is initialized.
    @classmethod
    async def create_instance(cls,db_client):
        await cls.create_index(db_client)
        model = cls(db_client)
        return model

    @staticmethod
    async def create_index(db_client):
        collection = db_client[DatabaseEnums.PROJECTS.value]
        for index in Project.get_indexes():
            await collection.create_index(
                index["keys"],
                name=index["name"],
                **index["options"]
            )
                
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

    async def get_projects(self, page: int=1, page_size: int=10):

        # count total number of documents
        documents_count = await self.collection.count_documents({})

        # calculate total number of pages
        total_pages = math.ceil( documents_count / page_size)

        cursor = self.collection.find().skip( (page-1) * page_size ).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )

        return projects, total_pages



    
