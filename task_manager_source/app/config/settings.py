from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Existing settings...
    
    wfo_days_per_month: int = 10


settings = Settings()