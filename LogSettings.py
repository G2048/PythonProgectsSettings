import json
import logging.config
import re

DEBUG = 'DEBUG'
COUNTER = 0
LOG_LEVEL = DEBUG or 'INFO'
SQL_LEVEL = DEBUG or 'WARNING'


class JSONFormatter(logging.Formatter):
    _pattern = re.compile(r'%\((\w+)\)s')

    def formatMessage(self, record) -> str:
        global COUNTER
        ready_message: dict = {}
        values = record.__dict__

        COUNTER += 1
        logger_name: str = values['name']
        ready_message['app.name'] = 'appname'.lower()
        ready_message['app.version'] = '1.0.0'
        ready_message['app.logger'] = logger_name
        ready_message['time'] = self.formatTime(record, self.datefmt)
        ready_message['level'] = values.get('levelname')
        ready_message['log_id']: int = COUNTER

        if record.exc_info:
            ready_message['exc_text'] = self.formatException(record.exc_info)
        if record.stack_info:
            ready_message['stack'] = self.formatStack(record.stack_info)

        for value_name in self._pattern.findall(self._fmt):
            value = values.get(value_name)
            ready_message.update({value_name: value})

        if logger_name.startswith('uvicorn') and len(record.args) == 5:
            ready_message.pop('message', None)
            ready_message['client_addr'] = record.args[0]
            ready_message['method'] = record.args[1]
            ready_message['path'] = record.args[2]
            ready_message['http_version'] = record.args[3]
            ready_message['status'] = record.args[4]

        return json.dumps(ready_message)


class RouterFilter(logging.Filter):
    endpoints = ('/metrics', '/health')

    def filter(self, record) -> bool:
        assert type(record.args) is tuple
        return not (len(record.args) > 2 and record.args[2] in self.endpoints)


LogConfig = {
    'version': 1,
    'disable_existing_loggers': False,
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
            'format': '%(filename)s::%(lineno)s::%(message)s',
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
            'stream': 'ext://sys.stderr',
            'formatter': 'details',
            'filters': ['router'],
        },
        'json': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'stream': 'ext://sys.stderr',
            'formatter': 'json',
            'filters': ['router'],
        },
    },
    'loggers': {
        'root': {
            'level': 'NOTSET',
        },
        'consolemode': {
            'level': LOG_LEVEL,
            'handlers': ['json'],
        },
        'asyncio': {
            'level': LOG_LEVEL,
            'handlers': ['json'],
        },
        'sqlalchemy.engine': {
            'level': SQL_LEVEL,
            'handlers': ['json'],
        },
        'sqlalchemy.pool': {
            'level': SQL_LEVEL,
            'handlers': ['json'],
        },
        'uvicorn': {
            'handlers': ['json'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['json'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'uvicorn.access': {
            'handlers': ['json'],
            'level': LOG_LEVEL,
            'propagate': False
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
    except EOFError:
        logger.critical('CRITICAL MESSAGE', exc_info=True)

    try:
        raise EOFError('EOF!')
    except:
        logger.exception('hello world')
