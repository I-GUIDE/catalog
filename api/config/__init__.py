from functools import lru_cache
from typing import Any

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# had to use load_dotenv() to get the env variables to work during testing
load_dotenv()


class Settings(BaseSettings):
    database_name: str
    db_username: str
    db_password: str
    db_host: str
    db_protocol: str
    testing: bool = False

    oidc_issuer: str
    hydroshare_meta_read_url: HttpUrl
    hydroshare_file_read_url: HttpUrl

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.testing:
            self.database_name = f"{self.database_name}"
        self.hydroshare_meta_read_url = str(self.hydroshare_meta_read_url)
        self.hydroshare_file_read_url = str(self.hydroshare_file_read_url)

    @property
    def db_connection_string(self):
        return f"{self.db_protocol}://{self.db_username}:{self.db_password}@{self.db_host}/?retryWrites=true&w=majority"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings():
    return Settings()
