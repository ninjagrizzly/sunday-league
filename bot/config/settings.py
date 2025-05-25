from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot Configuration
    bot_token: str = Field(..., env="BOT_TOKEN")
    bot_name: str = Field(default="FootballTournamentBot", env="BOT_NAME")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Paths
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    log_dir: Path = Field(default=Path("./logs"), env="LOG_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Bot Limits
    max_teams: int = Field(default=20, env="MAX_TEAMS")
    max_rounds: int = Field(default=20, env="MAX_ROUNDS")
    max_additional_rounds: int = Field(default=10, env="MAX_ADDITIONAL_ROUNDS")
    
    # Security
    allowed_users: Optional[List[int]] = Field(default=None, env="ALLOWED_USERS")
    admin_users: Optional[List[int]] = Field(default=None, env="ADMIN_USERS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_directories()
    
    def create_directories(self) -> None:
        """Create necessary directories"""
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)


settings = Settings()
