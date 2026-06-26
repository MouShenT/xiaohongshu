"""配置管理"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "xhs-ai-service"
    debug: bool = True

    # MySQL
    mysql_host: str = "192.168.229.149"
    mysql_port: int = 3306
    mysql_user: str = "xhs_app"
    mysql_password: str = "xhs_app_2024!"
    mysql_database: str = "xhs_platform"

    # Redis
    redis_host: str = "192.168.229.149"
    redis_port: int = 6379

    # LLM API Keys
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    qwen_api_key: str = ""

    # Qdrant
    qdrant_host: str = "192.168.229.149"
    qdrant_port: int = 6333

    # RabbitMQ
    rabbitmq_host: str = "192.168.229.149"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "xhs_admin"
    rabbitmq_password: str = "rabbit123!"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
