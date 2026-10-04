from fastapi import APIRouter,Request, status , Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from sqlalchemy import text
from .request_schemes import ReadinessResponse
from database.database_manager import get_db
health_router = APIRouter(prefix="/health", tags=["health checks"])
@health_router.get("/live")
async def is_alive():
    return {
        "status": "live"
    }


@health_router.get('/ready' , response_model=ReadinessResponse)
async def readiness_check(request: Request, db_client: AsyncSession = Depends(get_db)):
    vector_db_provider = request.app.vector_db_provider
    db_healthy = True
    vector_db_provider_healthy = True

    try:
        await db_client.execute(text("SELECT 1"))
    except Exception:
        db_healthy = False

    try:
        await vector_db_provider.connect()
    except Exception:
        vector_db_provider_healthy = False

    healthy = db_healthy and vector_db_provider_healthy

    return JSONResponse(
        content={
            "status": "ok" if healthy else "unhealthy",
            "dependencies": {
                "db": "ok" if db_healthy else "unhealthy",
                "vectordb": "ok" if vector_db_provider_healthy else "unhealthy",
            },
        },
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
    )