from pydantic_settings import BaseSettings
import os # Import the os module to handle file paths

# Get the directory of the current file (config.py is in 'backend/')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    # This variable will hold your PostgreSQL connection string
    DATABASE_URL: str
    AWS_ACCESS_KEY_ID: str = "Update"
    AWS_SECRET_ACCESS_KEY: str = "Update"

    class Config:
        # CRITICAL FIX: We join the BASE_DIR path with the filename '.env' 
        # to ensure the path correctly resolves to C:\projects\fut\backend\.env
        env_file = os.path.join(BASE_DIR, ".env")
        env_file_encoding = "utf-8"

settings = Settings()
print(f"[config] DATABASE_URL={settings.DATABASE_URL}")  # temporary: verify user/db
