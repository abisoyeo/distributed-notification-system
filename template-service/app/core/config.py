from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings
import secrets
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRE_DATABASE_URL = os.getenv('POSTGRE_DATABASE_URL')
if not POSTGRE_DATABASE_URL:
    raise Exception('DATABASE URL NOT SET')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='../.env',
        env_ignore_empty=True,
        extra='ignore'
    )
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description='App secret key'
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    PROJECT_NAME: str = 'Template Service'
    DATABASE_URL: str = POSTGRE_DATABASE_URL

settings = Settings()