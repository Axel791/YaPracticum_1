from pydantic import BaseSettings


class Settings(BaseSettings):
    project_slug: str
    api_v1_str: str

    kafka_broker_url: str
    schema_registry_url: str
    number_partitions: int

    jwt_secret_key: str
    algorithm: str

    sentry_dsn: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
