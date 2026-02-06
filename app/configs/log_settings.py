import json
import logging.config
import logging.handlers
import queue
import re
import uuid
from contextvars import ContextVar
from logging import Logger

"""
Description: Log settings
Example of usage:

# Add in main.py
>>> from app.configs import (
    get_appsettings,
    get_database_settings,
    get_logger,
)

>>> set_appname(get_appsettings().APP_NAME)
>>> set_appversion(get_appsettings().APP_VERSION)
>>> set_debug_level(get_appsettings().DEBUG)

# In another module:
>>> import logging
>>> logger = logging.getLogger("stdout")
>>> logger.debug("hello world")
>>> logger.info("hello world")
>>> logger.warning("hello world")


# If you are using the uvicorn:
>>> from log_config import LogConfig
...
>>> if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=LogConfig)

"""


DEBUG: bool = False
LOG_LEVEL = "INFO"
SQL_LEVEL = "WARNING"
_appname = "appname"
_version = "1.0.0"


def set_appversion(version: str):
    global _version
    _version = version


class JSONFormatter(logging.Formatter):
    _pattern = re.compile(r"%\((\w+)\)s")
    COUNTER = 0
    _req_id = ContextVar("req_id", default=uuid.uuid4().hex[:10])

    def formatMessage(self, record) -> str:
        global _appname
        global _version
        ready_message: dict = {}
        values = record.__dict__

        self.COUNTER += 1
        logger_name: str = values["name"]
        ready_message["app.name"] = _appname
        ready_message["app.version"] = _version
        ready_message["app.logger"] = logger_name
        ready_message["time"] = self.formatTime(record, self.datefmt)
        ready_message["level"] = values.get("levelname")
        ready_message["log_id"]: int = self.COUNTER
        ready_message["message"] = str(values["message"])

        if not values.get("req_id"):
            values["req_id"] = self._req_id.get()

        if record.exc_info:
            ready_message["exc_text"] = self.formatException(record.exc_info)
        if record.stack_info:
            ready_message["stack"] = self.formatStack(record.stack_info)

        for value_name in self._pattern.findall(self._fmt):
            value = values.get(value_name)
            ready_message.update({value_name: value})

        if logger_name.startswith("uvicorn") and record.args and len(record.args) == 5:
            ready_message.pop("message", None)
            ready_message["client_addr"] = record.args[0]
            ready_message["method"] = record.args[1]
            ready_message["path"] = record.args[2]
            ready_message["http_version"] = record.args[3]
            ready_message["status"] = record.args[4]

        return json.dumps(ready_message, ensure_ascii=False)


class RouterFilter(logging.Filter):
    endpoints = ("/metrics", "/health")

    def filter(self, record) -> bool:
        return record.args is None or (
            not len(record.args) > 2 and record.args[2] in self.endpoints
        )


class AutoStartQueueListener(logging.handlers.QueueListener):
    def __init__(self, queue, *handlers, respect_handler_level=False):
        super().__init__(queue, *handlers, respect_handler_level=respect_handler_level)
        # Start the listener immediately.
        self.start()


class RequestIdFilter(logging.Filter):
    def __init__(self, name=""):
        self.req_id = ContextVar("req_id", default=None)
        super().__init__(name)

    def filter(self, record):
        if not self.req_id.get():
            self.req_id.set(uuid.uuid4().hex[:10])
        record.req_id = self.req_id.get()
        return True


LogConfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "details": {
            "class": "logging.Formatter",
            "format": "%(asctime)s::%(levelname)s::%(filename)s::%(levelno)s::%(lineno)s::%(message)s",  # noqa: E501
            "incremental": True,
            "encoding": "UTF-8",
        },
        "json": {
            # '()': 'LogSettings.JSONFormatter',
            "()": JSONFormatter,
            "format": "%(process)d::%(filename)s::%(lineno)s::%(message)s::%(req_id)s",
            # "format": "%(process)d::%(filename)s::%(lineno)s::%(message)s",
        },
    },
    "filters": {
        "router": {
            "()": RouterFilter,
        },
        "req_id": {
            "()": RequestIdFilter,
        },
    },
    "handlers": {
        "rotate": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_appname}.log",
            "mode": "w",
            "level": "DEBUG",
            "maxBytes": 204800,
            "backupCount": 15,
            "formatter": "details",
            "filters": ["router"],
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": "ext://sys.stderr",
            "formatter": "details",
            "filters": ["router"],
        },
        "json": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": "ext://sys.stderr",
            "formatter": "json",
            "filters": ["router"],
        },
        "jsonq": {
            "class": "logging.handlers.QueueHandler",
            "queue": {
                "()": queue.Queue,
                "maxsize": -1,
            },
            "level": "DEBUG",
            "listener": AutoStartQueueListener,
            "handlers": ["json"],
        },
        # 'handlers': ['cfg://handlers.json', 'cfg://handlers.console'],
    },
    "loggers": {
        "": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "stdout": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "app": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "worker": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "faststream": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "faststream.access": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "faststream.access.rabbit": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "asyncio": {
            "level": LOG_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        # "logfile": {"level": LOG_LEVEL, "handlers": ["rotate"], "propagate": False},
        "uvicorn": {
            "handlers": ["jsonq"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.error": {
            # DISABLE logger  because something redefine log level to debug... it's too verbose
            "handlers": ["jsonq"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["jsonq"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": SQL_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "sqlalchemy.pool": {
            "level": SQL_LEVEL,
            "handlers": ["jsonq"],
            "propagate": False,
        },
        "httpx": {
            "level": "WARNING",
            "handlers": ["jsonq"],
            "propagate": False,
        },
    },
}


class CustomLogger(Logger):
    def refresh_req_id(self):
        self.filters = []
        self.addFilter(RequestIdFilter())


def get_logger(name="app") -> CustomLogger:
    logging.setLoggerClass(CustomLogger)
    logging.config.dictConfig(LogConfig)
    logger: CustomLogger = logging.getLogger(name)
    return logger


def set_appname(name: str):
    global _appname
    _appname = name
    LogConfig["handlers"]["rotate"]["filename"] = f"{name}.log"


def set_debug_level(debug: bool):
    if debug:
        for logger in LogConfig["loggers"].values():
            logger["level"] = "DEBUG"


if __name__ == "__main__":
    logger = get_logger()

    logger.debug("hello world")
    logger.info("ПРИВЕТ МИР!")
    logger.warning("hello world")
    logger.refresh_req_id()

    log = logging.getLogger("nonexist")
    log.refresh_req_id()
    log.debug("hello world")
    log.info("hello world")
    log.warning("hello world")
    log.critical("hello world")

    log2 = logging.getLogger("nonexist2")
    # log2.refresh_req_id()
    log2.debug("hello world")
    log2.info("hello world")
    log2.warning("hello world")
    log2.critical("hello world")

    try:
        logger.error("hello world")
        raise EOFError("EOF!")
    except EOFError:
        logger.critical("CRITICAL MESSAGE", exc_info=True)

    try:
        raise EOFError("EOF!")
    except Exception:
        logger.exception("hello world")
