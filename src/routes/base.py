from fastapi import APIRouter,Depends
from helpers.config import Settings, get_settings
import os

router = APIRouter(prefix="/api", tags=["API Endpoints"])

@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.get('/entery')
async def entery():
    return {"message": "Welcome to the entry point of the API!"}

@router.get('/info')
async def info(settings: Settings = Depends(get_settings)):
    return {'app_name': settings.APP_NAME, 'app_version': settings.APP_VERSION}