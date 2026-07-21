from fastapi import APIRouter,UploadFile,status,Depends
from controllers import DataController,ProjectController
from models import ResponseStatus
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
import aiofiles

router = APIRouter(prefix="/api/upload_data", tags=["data upload"])

@router.post("/upload{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    datacontroller = DataController()

    result = datacontroller.validate_file(file)

    if result.get(ResponseStatus.ERROR.value):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result
        )
    
    
    file_path = datacontroller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )[0]


    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):  # Read the file in chunks
            await f.write(chunk)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result
    )