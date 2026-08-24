from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_connect_user: str
    db_connect_pass: str
    db_connect_name: str
    db_connect_host: str
    db_connect_port: int

    steam_api_key: str
    stratz_api_key: str

    @property
    def database_url(self) -> str:
        return "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            self.db_connect_user,
            self.db_connect_pass,
            self.db_connect_host,
            self.db_connect_port,
            self.db_connect_name,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
