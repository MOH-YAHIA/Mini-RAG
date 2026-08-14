from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings): # act like validation layer.read and parse enviroment variables. if one variable has mismatch type. then it will raise an exception

    APP_NAME: str
    APP_VERSION: str
    ASSET_ALLOWED_TYPES: list[str]
    ASSET_MAX_SIZE: int
    ASSET_CHUNK_SIZE : int
    MONGODB_URL : str
    MONGODB_DATABASE : str

    PROVIDER : str
    OPENAI_BASE_URL : str
    OPENAI_BASE_API_KEY : str

                
    EMBEDDING_MODEL_ID : str
    EMBEDDING_DIM : int

    GENERATION_MODEL_ID : str
    GENERATION_DAFAULT_INPUT_MAX_CHARACTERS : str = None
    GENERATION_DAFAULT_OUTPUT_MAX_TOKENS : str = None
    GENERATION_DAFAULT_TEMPERATURE : float = None


    VECTOR_DB_PROVIDER : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD : str

    model_config=SettingsConfigDict(
        env_file = ".env" #src is the import root 
    )

def get_settings():
    return Settings()