import json
import logging
import re


class JSONFormatter(logging.Formatter):
    _pattern = re.compile('%\((\w+)\)s')

    def formatMessage(self, record):
        ready_message: dict = {}
        values = record.__dict__

        for value in self._pattern.findall(self._fmt):
            ready_message.update({value: values.get(value)})

        return json.dumps(ready_message)


LogConfig = {
    'version': 1,
    "disable_existing_loggers": False,
    'formatters': {
        'details': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s::%(levelname)s::%(filename)s::%(levelno)s::%(lineno)s::%(message)s',
            'incremental': True,
            'encoding': 'UTF-8',
        },
        'json': {
            # '()': 'LogSettings.JSONFormatter',
            '()': JSONFormatter,
            'format': '%(asctime)s::%(levelname)s::%(filename)s::%(levelno)s::%(lineno)s::%(message)s',
        },
    },
    'handlers': {
        'rotate': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log.log',
            'mode': 'w',
            'level': 'DEBUG',
            'maxBytes': 204800,
            'backupCount': 3,
            'formatter': 'details',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            "stream": "ext://sys.stderr",
            'formatter': 'details',
        },
        'json_console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            "stream": "ext://sys.stderr",
            'formatter': 'json',
        },
    },
    'loggers': {
        'root': {
            'level': 'NOTSET',
            'handlers': ['rotate'],
        },
        'consolemode': {
            'level': 'DEBUG',
            'handlers': ['json_console'],
        },
        'sqlalchemy.engine': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'sqlalchemy.pool': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO"
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
    },
}

if __name__ == '__main__':
    import logging.config

    logging.config.dictConfig(LogConfig)
    logger = logging.getLogger('consolemode')

    logger.debug('hello world')
    logger.info('hello world')
    logger.warning('hello world')
    logger.error('hello world')
    logger.critical('hello world')
