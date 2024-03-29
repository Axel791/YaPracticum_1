from pydantic import BaseSettings


class Settings(BaseSettings):
    project_slug: str
    api_v1_str: str

    etl_host: str
    etl_port: str
    etl_schema: str

    redis_port: str
    redis_host: str

    authentication_url: str

    film_cache_expire_in_second: int = 60

    default_page_size: int = 10

    sentry_dsn: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
