from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings): # act like validation layer.read and parse enviroment variables. if one variable has mismatch type. then it will raise an exception

    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE : int
    MONGODB_URL : str
    MONGODB_DATABASE : str

    model_config=SettingsConfigDict(
        env_file = ".env" #src is the import root 
    )

def get_settings():
    return Settings()