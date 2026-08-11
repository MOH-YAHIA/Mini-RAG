from fastapi import APIRouter,UploadFile,status,Depends,Request
from controllers import AssetController, ProcessController
from models import ResponseStatus,AssetTypeEnums, Chunk, ProjectModel, ChunkModel, AssetModel, Asset
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
import aiofiles
from .request_schemes import ProcessRequest
import logging


logger = logging.getLogger('uvicorn.error')

router = APIRouter(prefix="/data", tags=["data house"])

@router.post("/upload{project_id}")
async def upload_data(request: Request ,project_id: str, asset: UploadFile, app_settings: Settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(request.app.mongodb_client)
    project = await project_model.find_project(project_id)

    asset_controller = AssetController()
    result = asset_controller.validate_asset(asset)

    if result !=  ResponseStatus.AssetValidateSuccess.value:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=str(result)
        )
    
    
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

    asset_model = await AssetModel.create_instance(request.app.mongodb_client)
    asset = Asset(
        asset_project_id=project.id,
        asset_name=asset_name,
        asset_type=AssetTypeEnums.File.value,
        asset_size=os.path.getsize(asset_path)

    )
    asset = await asset_model.insert_asset(asset)


    result={'signal' : str(ResponseStatus.AssetUploadSuccess.value)}
    result['asset_name']=asset_name
    result['project_id']=str(project.id)    
    result['asset_id']=str(asset.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result,
    )

@router.post("/process{project_id}")
async def process_data(request: Request, project_id: str, process_request:ProcessRequest):

    asset_name = process_request.asset_name
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.overlap_size
    do_reset = process_request.do_reset
    
    project_model = await ProjectModel.create_instance(request.app.mongodb_client)
    asset_model = await AssetModel.create_instance(request.app.mongodb_client)
    chunk_model = await ChunkModel.create_instance(request.app.mongodb_client)


    project = await project_model.find_project(project_id)
    if do_reset:
        _ = await chunk_model.delete_chunks_by_project_id(project.id)

    
    
    assets = []
    if asset_name:
        assets = [await asset_model.get_asset(asset_project_id=project.id, asset_name=asset_name)]
        if assets[0] is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=str(ResponseStatus.AssetNotFound.value)
            )
    else:
        assets = await asset_model.get_project_assets(asset_project_id=project.id, asset_type=AssetTypeEnums.File.value)
        if len(assets) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=str(ResponseStatus.AssetNotFound.value)
            )


    process_controler = ProcessController(project_id)
    total_chunks_created = 0
    successful_asset_process = 0
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
    

        chunk_count = await chunk_model.insert_chunks(ready_chunks)
        total_chunks_created += chunk_count
        successful_asset_process+=1 

    result = {'signal': str(ResponseStatus.AssetProcessSuccess.value)}
    result['total_chunks_created']=total_chunks_created
    result['successful_asset_process']=successful_asset_process


    return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
