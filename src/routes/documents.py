from fastapi import APIRouter,UploadFile,status,Depends,Request
from controllers import AssetController, ProcessController
from database.database_manager import get_db
from repositories import ProjectRepository,AssetRepository,ChunkRepository
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
import aiofiles
from models.db_schemes import Asset, Chunk
from models.enums import AssetTypeEnums
from .request_schemes import ProcessRequest,ProcessResponse, AssetUploadResponse
import logging
from .enums.ResponseEnums import ResponseStatus
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('uvicorn.error')

documents_router = APIRouter(prefix="/documents", tags=["data house"])

@documents_router.post("/upload/{project_id}", response_model=AssetUploadResponse)
async def upload_data(request: Request ,project_id: str, asset: UploadFile, app_settings: Settings = Depends(get_settings), db_client: AsyncSession = Depends(get_db)):

    project_repository = ProjectRepository(db_client)
    project = await project_repository.find_project(project_id)

    asset_controller = AssetController()
    result = asset_controller.validate_asset(asset)

    if result !=  ResponseStatus.AssetValidateSuccess.value:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=str(result)
        )
    # response_model validates normal return values, not manually constructed Response objects such as JSONResponse.
    # so when we pass JSONResponse. fastapi doesn't validate it throw response_model. it return it directly.
    
    
    asset_path,asset_name = asset_controller.generate_unique_assetpath(
        orig_asset_name=asset.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(asset_path, 'wb') as f:
            while chunk := await asset.read(app_settings.ASSET_CHUNK_SIZE):  # Read the file in chunks
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseStatus.AssetUploadFailed.value
        )

    asset_repository =  AssetRepository(db_client)
    asset = Asset(
        asset_project_id=project.id,
        asset_name=asset_name,
        asset_type=AssetTypeEnums.File.value,
        asset_size=os.path.getsize(asset_path)

    )
    asset = await asset_repository.insert_asset(asset)


    return AssetUploadResponse(
        status=ResponseStatus.AssetUploadSuccess.value,
        asset_name=asset_name,
        project_id=str(project.id),
        asset_id=str(asset.id),
    )

@documents_router.post("/process/{project_id}", response_model=ProcessResponse)
async def process_data(request: Request, project_id: str, process_request:ProcessRequest, db_client: AsyncSession = Depends(get_db)):

    asset_name = process_request.asset_name
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.overlap_size
    do_reset = process_request.do_reset
    
    project_repository =  ProjectRepository(db_client)
    asset_repository =  AssetRepository(db_client)
    chunk_repository =  ChunkRepository(db_client)


    project = await project_repository.find_project(project_id)
    if do_reset:
        _ = await chunk_repository.delete_chunks_by_project_id(project.id)

    
    
    assets = []
    if asset_name:
        assets = [await asset_repository.get_asset(asset_project_id=project.id, asset_name=asset_name)]
        if assets[0] is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=str(ResponseStatus.AssetNotFound.value)
            )
    else:
        assets = await asset_repository.get_project_assets(asset_project_id=project.id, asset_type=AssetTypeEnums.File.value)
        if len(assets) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=str(ResponseStatus.AssetNotFound.value)
            )


    process_controler = ProcessController(project_id)
    total_chunks_created = 0
    successful_asset_processed = 0
    for asset in assets:
        asset_name = asset.asset_name
        documents = process_controler.load_document(asset_name)
        if documents is None:
            logger.error(f"Failed to load documents for asset: {asset_name}")
            continue  # Skip to the next asset if loading fails

        chunks = process_controler.split_documents(documents, chunk_size, chunk_overlap)
        if chunks is None:
            logger.error(f"Failed to split documents for asset: {asset_name}")
            continue  # Skip to the next asset if splitting fails

        ready_chunks = [Chunk(
            chunk_project_id=project.id,
            chunk_asset_id=asset.id,
            chunk_text=doc.page_content,
            chunk_metadata=doc.metadata,
            chunk_order=i+1
        ) 
        for i,doc in enumerate(chunks)]
    

        chunk_count = await chunk_repository.insert_chunks(ready_chunks)
        total_chunks_created += chunk_count
        successful_asset_processed+=1 


    return ProcessResponse(
        status=ResponseStatus.AssetProcessSuccess.value,
        total_chunks_created=total_chunks_created,
        successful_asset_processed=successful_asset_processed
    )
