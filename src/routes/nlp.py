from fastapi import APIRouter,status,Depends,Request
from controllers import  NlpController
from models import ResponseStatus, ProjectModel, ChunkModel, AssetModel
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from .request_schemes import EmbedRequest,SearchRequest
import logging


logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(prefix="/nlp", tags=["nlp house"])

@nlp_router.post("/embed{project_id}")
async def embed(request: Request , project_id: str, embed_request: EmbedRequest, app_settings: Settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.mongodb_client
    )
    chunk_model = await ChunkModel.create_instance(
            db_client=request.app.mongodb_client
        )
    
    if not await project_model.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )
    project = await project_model.find_project(project_id)

    if embed_request.asset_name :
        asset_model = await AssetModel.create_instance(
            db_client=request.app.mongodb_client
        )
        if not await asset_model.dose_asset_exist(embed_request.asset_name):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.AssetNotFound.value
                }
            )
        asset = await asset_model.get_asset(asset_project_id=project.id, asset_name=embed_request.asset_name)
        chunks = await chunk_model.get_chunks_by_asset_id(asset.id)

    else:
        chunks = await chunk_model.get_chunks_by_project_id(project.id)
          
    index_controller = NlpController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)
    inserted = index_controller.embed_chunks(project = project, chunks = chunks, 
                                                 embedding_size=app_settings.EMBEDDING_DIM, 
                                                 distance_method=app_settings.EMBEDDING_DISTANCE_METHOD)

    
    if inserted:
         return JSONResponse(
             status_code=status.HTTP_200_OK,
             content={
                 "signal": ResponseStatus.ChunksIndexedSuccess.value
             }
         )
 
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "signal": ResponseStatus.ChunksIndexedFaild.value
        }
    )

    

@nlp_router.post("/search{project_id}")
async def search(request: Request , project_id: str, search_request: SearchRequest ,app_settings: Settings = Depends(get_settings)):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.mongodb_client
    )

    if not await project_model.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )

    project = await project_model.find_project(project_id)
    nlp_controller = NlpController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)
    results = nlp_controller.search_vector_db(project=project,text=search_request.query,limit=2)

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.VECTORDB_SEARCH_FAILD.value
                }
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.VECTORDB_SEARCH_SUCCESS.value,
            "results": [ result.dict()  for result in results ]
        }
    )


@nlp_router.get("/collection_info{project_id}")
async def get_collection_info(request: Request , project_id: str):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.mongodb_client
    )

    if not await project_model.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )

    project = await project_model.find_project(project_id)
    nlp_controller = NlpController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)
    collection_info = nlp_controller.get_project_collection_info(project=project)

    if not collection_info:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.CollectionNotFound.value
                }
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.CollectionInfoSuccess.value,
            "results": collection_info
        }
    )

@nlp_router.post("/answer{project_id}")
async def search(request: Request , project_id: str, search_request: SearchRequest ,app_settings: Settings = Depends(get_settings)):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.mongodb_client
    )

    if not await project_model.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )

    project = await project_model.find_project(project_id)
    nlp_controller = NlpController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)

    answer, chat_history = nlp_controller.answer_rag_question(locale=app_settings.LOCALE,project=project,question=search_request.query,limit=2)

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.RagAnswerFaild.value
                }
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.RagAnswerSuccess.value,
            "answer": answer,
            "chat_history": chat_history
        }
    )