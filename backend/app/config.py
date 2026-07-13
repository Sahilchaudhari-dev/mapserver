from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "geodb"
    db_user: str = "geouser"
    db_password: str = "sahil"
    tile_server_url: str = "http://localhost"
    api_port: int = 8080

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()