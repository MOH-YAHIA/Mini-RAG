from .BaseControler import BaseController
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_project_folder_path(self, project_id):
        project_path = os.path.join(self.projects_directory,project_id)

        os.makedirs(project_path, exist_ok=True)

        return project_path