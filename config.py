
import logging


DB_NAME = "golden-eye.sqlite"

LOGGER_CONFIG = dict(level=logging.DEBUG, #вывод debug log-ов
# LOGGER_CONFIG = dict(level=logging.INFO,  #вывод только info log-ов
# LOGGER_CONFIG = dict(level=logging.WARN,    #нет log-ов уровня WARN
                     file="app.log",
                     formatter=logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s:%(message)s")
                     )

HTTP_TIMEOUT = 15
IP_LIST = ["127.0.0.1", "10.10.0.175"]
LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': "[%(asctime)s] [%(levelname)s] - %(name)s: %(message)s",
        },
    },

    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'new.log',
        },
    },
    'loggers': {
        'GoldenEye': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
        'Api': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
        'Tasks': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
    },
}


