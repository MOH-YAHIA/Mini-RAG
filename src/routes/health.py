from fastapi import APIRouter,Request, status
from fastapi.responses import JSONResponse
from .request_schemes import ReadinessResponse

health_router = APIRouter(prefix="/health", tags=["health checks"])

@health_router.get("/live")
async def is_alive():
    return {
        "status": "live"
    }


@health_router.get('/ready' , response_model=ReadinessResponse)
async def readiness_check(request: Request):
    mongodb_conn = request.app.mongodb_conn
    vector_db_provider = request.app.vector_db_provider

    mongodb_healthy = True
    vector_db_provider_healthy = True

    try:
        await mongodb_conn.admin.command("ping")
    except Exception:
        mongodb_healthy = False

    try:
        vector_db_provider.connect()
    except Exception:
        vector_db_provider_healthy = False

    healthy = mongodb_healthy and vector_db_provider_healthy

    return JSONResponse(
        content={
            "status": "ok" if healthy else "unhealthy",
            "dependencies": {
                "mongodb": "ok" if mongodb_healthy else "unhealthy",
                "vectordb": "ok" if vector_db_provider_healthy else "unhealthy",
            },
        },
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
    )