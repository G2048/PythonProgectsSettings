import json
import logging.config
import re


class JSONFormatter(logging.Formatter):
    _pattern = re.compile('%\((\w+)\)s')

    def formatMessage(self, record) -> str:
        ready_message: dict = {}
        values = record.__dict__

        if record.exc_info:
            ready_message['exc_text'] = self.formatException(record.exc_info)
        if record.stack_info:
            ready_message['stack'] = self.formatStack(record.stack_info)

        for value in self._pattern.findall(self._fmt):
            ready_message.update({value: values.get(value)})
        # ready_message.update({'args': record.args})

        return json.dumps(ready_message)


class RouterFilter(logging.Filter):
    endpoints = ('/metrics', '/health')

    def filter(self, record) -> bool:
        assert type(record.args) is tuple
        return not (len(record.args) > 2 and record.args[2] in self.endpoints)


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
    'filters': {
        'router': {
            '()': RouterFilter,
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
            'filters': ['router'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            "stream": "ext://sys.stderr",
            'formatter': 'details',
            'filters': ['router'],
        },
        'json_console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            "stream": "ext://sys.stderr",
            'formatter': 'json',
            'filters': ['router'],
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


def get_logger(name=''):
    logging.config.dictConfig(LogConfig)
    return logging.getLogger(name)


if __name__ == '__main__':
    logger = get_logger('consolemode')

    logger.debug('hello world')
    logger.info('hello world')
    logger.warning('hello world')

    try:
        logger.error('hello world')
        raise EOFError('EOF!')
    except EOFError as e:
        logger.critical('CRITICAL MESSAGE', exc_info=True)

    try:
        raise EOFError('EOF!')
    except:
        logger.exception('hello world')
