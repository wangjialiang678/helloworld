"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 飞书配置
    feishu_app_id: str = ""
    feishu_app_secret: str = ""

    # AI配置
    qwen_api_key: str = ""

    # 服务配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS配置
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
