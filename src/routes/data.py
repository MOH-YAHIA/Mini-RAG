from fastapi import APIRouter,UploadFile,status,Depends
from controllers import DataController,ProjectController, ProcessControler
from models import ResponseStatus
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
import aiofiles
from .schemas.data import ProcessRequest
import logging

logger = logging.getLogger('uvicorn.error')

router = APIRouter(prefix="/data", tags=["data upload"])

@router.post("/upload{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    datacontroller = DataController()

    result = datacontroller.validate_file(file)

    if result.get(ResponseStatus.ERROR.value):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=result
        )
    
    
    file_path,file_name = datacontroller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):  # Read the file in chunks
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={ResponseStatus.ERROR.value: ResponseStatus.FileUploadFailed.value}
        )
    result['file_id']=file_name
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result
    )

@router.post("/process{project_id}")
async def process_data(project_id: str, process_request:ProcessRequest):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.overlap_size

    process_controler = ProcessControler(project_id)
    documents = process_controler.load_document(file_id)
    chunks = process_controler.split_documents(documents, chunk_size, chunk_overlap)

    if chunks is None or len(chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={ResponseStatus.ERROR.value: ResponseStatus.NoChunksCreated.value}
        )
    
    return chunks
