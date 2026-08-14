from helpers.config import Settings, get_settings
import os
import random
import string

class BaseController:
    def __init__(self, settings: Settings = get_settings()):
        self.settings = settings

        self.asset_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),'assets')
        self.projects_directory = os.path.join(self.asset_directory ,'projects')




    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_vector_db_path(self, db_name: str):
        path = os.path.join(self.asset_directory ,db_name)
        os.makedirs(path, exist_ok=True)
        return path
