from fastapi import APIRouter,status,Depends,Request
from controllers import  RagController
from repositories import ProjectRepository,AssetRepository,ChunkRepository
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from routes.enums.ResponseEnums import ResponseStatus
from .request_schemes import EmbedRequest,RetrieveRequest, EmbedResponse, RetriveResponse, CollectionInfoResponse, ChatResponse
import logging
from database.database_manager import get_db
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('uvicorn.error')

rag_router = APIRouter(prefix="/rag", tags=["rag house"])

@rag_router.post("/embed/{project_id}", response_model=EmbedResponse)
async def embed(request: Request , project_id: str, embed_request: EmbedRequest, app_settings: Settings = Depends(get_settings), db_client: AsyncSession = Depends(get_db)):

    project_repository = ProjectRepository(db_client)
    chunk_repository = ChunkRepository(db_client)

    if not await project_repository.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )
    project = await project_repository.find_project(project_id)

    if embed_request.asset_name :
        asset_repository = AssetRepository(
            db_client
        )
        if not await asset_repository.dose_asset_exist(embed_request.asset_name):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.AssetNotFound.value
                }
            )
        asset = await asset_repository.get_asset(asset_project_id=project.id, asset_name=embed_request.asset_name)
        chunks = await chunk_repository.get_chunks_by_asset_id(asset.id)

    else:
        chunks = await chunk_repository.get_chunks_by_project_id(project.id)
          
    rag_controller = RagController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)
    inserted = await rag_controller.embed_chunks(project = project, chunks = chunks, 
                                                 embedding_size=app_settings.EMBEDDING_DIM, 
                                                 distance_method=app_settings.EMBEDDING_DISTANCE_METHOD)

    if not inserted:
         return JSONResponse(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 content={
                     "signal": ResponseStatus.ChunksEmbeddedFaild.value
                 }
             )
    
    return EmbedResponse(
        status= ResponseStatus.ChunksEmbeddedSuccess.value
    )
 

    

@rag_router.post("/retrieve/{project_id}", response_model=RetriveResponse)
async def search(request: Request , project_id: str, retrieve_request: RetrieveRequest ,app_settings: Settings = Depends(get_settings), db_client: AsyncSession = Depends(get_db)):
    project_repository = ProjectRepository(
        db_client
    )

    if not await project_repository.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )

    project = await project_repository.find_project(project_id)
    nlp_controller = RagController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)
    retrieved_documents_with_scores = await nlp_controller.search_vector_db(project=project,text=retrieve_request.query,limit=retrieve_request.limit)

    if not retrieved_documents_with_scores:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.VectorDBRetrieveFaild.value
                }
            )

    return RetriveResponse(
        status= ResponseStatus.VectorDBRetrieveSuccess.value,
        retrieved_documents_with_scores=retrieved_documents_with_scores
    )


@rag_router.get("/collection_info/{project_id}", response_model=CollectionInfoResponse)
async def get_collection_info(request: Request , project_id: str, db_client: AsyncSession = Depends(get_db)):
    project_repository = ProjectRepository(
        db_client
    )

    if not await project_repository.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )

    project = await project_repository.find_project(project_id)
    rag_controller = RagController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)
    collection_info = await rag_controller.get_project_collection_info(project=project)

    if not collection_info:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.CollectionNotFound.value
                }
            )

    return CollectionInfoResponse(
        status= ResponseStatus.CollectionInfoSuccess.value,
        collection_info=collection_info["collection_info"],
        records_count=collection_info["records_count"],
    )

@rag_router.post("/chat/{project_id}", response_model=ChatResponse)
async def search(request: Request , project_id: str, retrieve_request: RetrieveRequest ,app_settings: Settings = Depends(get_settings), db_client: AsyncSession = Depends(get_db)):
    project_repository = ProjectRepository(
        db_client
    )

    if not await project_repository.does_project_exist(project_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.ProjectNotFound.value
                }
            )

    project = await project_repository.find_project(project_id)
    rag_controller = RagController(llm_provider=request.app.llm_provider, vector_db_provider=request.app.vector_db_provider)

    answer, chat_history = await rag_controller.answer_rag_question(locale=app_settings.LOCALE,project=project,question=retrieve_request.query,limit=retrieve_request.limit)

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.RagAnswerFaild.value
                }
            )

    return ChatResponse(
        status= ResponseStatus.RagAnswerSuccess.value,
        answer=answer,
        chat_history=chat_history
    )