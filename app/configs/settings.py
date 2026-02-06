from dotenv import load_dotenv

from app.core.configs import (
    AppSettings,
    DataBaseSettings,
    set_appname,
    set_appversion,
    set_debug_level,
)

load_dotenv()

_app_settings = AppSettings()
set_debug_level(_app_settings.debug)
set_appname(_app_settings.appname_log)  # ty: ignore
set_appversion(_app_settings.appversion)

_database_settings = DataBaseSettings()  # ty: ignore


def get_appsettings():
    return _app_settings


def get_database_settings():
    return _database_settings
