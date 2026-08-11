from helpers.config import Settings, get_settings
import os
import random
import string

class BaseController:
    def __init__(self, settings: Settings = get_settings()):
        self.settings = settings

        self.projects_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),'assets','projects')


    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))