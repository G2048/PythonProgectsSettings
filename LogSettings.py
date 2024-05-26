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
            'formatter': 'details',
        },
    },
    'loggers': {
        'root': {
            'level': 'NOTSET',
            'handlers': ['rotate'],
        },
        'consolemode': {
            'level': 'DEBUG',
            'handlers': ['console'],
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
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO"
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False
        },
    },
}
