from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #Present in .env file
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    UPLOAD_DIR:str = "upload_files"

    #JWT should last 1 hour
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    #aws
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore")

settings = Settings()