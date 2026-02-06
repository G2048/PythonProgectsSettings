from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .pyproject import ParserPyproject


class AppSettings(BaseSettings):
    appname: str = ParserPyproject.name
    appversion: str = ParserPyproject.version
    debug: bool = False

    @computed_field(return_type=str)
    def appname_log(self) -> str:
        return self.appname.lower().replace(" ", "_")


class DataBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG_")

    host: str
    port: str
    user: str
    dbname: str
    password: str
    engine: str | None = "psycopg"

    @computed_field(return_type=str)
    def pg_dsn(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
