import os
import re

from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus
from .ProjectController import ProjectController

class AssetController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_asset(self, asset: UploadFile):
        if asset.content_type not in self.settings.ASSET_ALLOWED_TYPES:
            return ResponseStatus.AssetTypeNotAllowed.value
        
        if asset.size  > self.settings.ASSET_MAX_SIZE * 1024 * 1024:
            return ResponseStatus.AssetSizeExceedsLimit.value

        return ResponseStatus.AssetValidateSuccess.value
    

    def generate_unique_assetpath(self, orig_asset_name: str, project_id: str):

        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_folder_path(project_id)

        cleaned_asset_name = self.get_clean_asset_name(
            orig_asset_name=orig_asset_name
        )

        new_asset_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_asset_name
        )

        while os.path.exists(new_asset_path):
            random_key = self.generate_random_string()
            new_asset_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_asset_name
            )

        return new_asset_path, random_key + "_" + cleaned_asset_name

    def get_clean_asset_name(self, orig_asset_name: str):

        # remove any special characters, except underscore and .
        cleaned_asset_name = re.sub(r'[^\w.]', '', orig_asset_name.strip())

        # replace spaces with underscore
        cleaned_asset_name = cleaned_asset_name.replace(" ", "_")

        return cleaned_asset_name