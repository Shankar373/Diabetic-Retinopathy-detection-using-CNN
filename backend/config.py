from pydantic import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    api_url: str = os.getenv('NEXT_PUBLIC_PYTHON_API_URL', 'http://localhost:8000')
    port: int = int(os.getenv('PORT', 8000))
    model_path: str = os.getenv('MODEL_PATH', './models/dr_model.h5')
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
