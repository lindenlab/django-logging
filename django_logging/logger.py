import logging
import logging.config
import os

import sys

from django.core.exceptions import ImproperlyConfigured

from . import settings

LOG_LEVEL = settings.LOG_LEVEL.upper()
LOG_HANDLERS = []

if settings.INFO_FILE_LOG:
    LOG_HANDLERS.append['default']
if settings.CONSOLE_LOG:
    LOG_HANDLERS.append('console')
if settings.DEBUG_FILE_LOG:
    LOG_HANDLERS.append('debug')
if settings.SQL_LOG:
    LOG_HANDLERS.append('sql')

if not LOG_HANDLERS:
    raise ImproperlyConfigured("At least one LOG_HANDLER must be enabled")

if not os.path.exists(settings.LOG_PATH) and (settings.INFO_FILE_LOG or settings.DEBUG_FILE_LOG or settings.SQL_LOG):
    try:
        os.makedirs(settings.LOG_PATH)
    except Exception as e:
        raise Exception('Unable to configure logger. Can\'t create LOG_PATH: {}'.format(settings.LOG_PATH))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': settings.DISABLE_EXISTING_LOGGERS,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s - %(created)s] file:%(module)s.py, func:%(funcName)s, ln:%(lineno)s: %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        },
        'sql': {
            'format': '[%(levelname)s - %(created)s] %(duration)s %(sql)s %(params)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'django_logging.handlers.ConsoleHandler',
            'formatter': 'verbose',
            'stream': sys.stderr
        },
        'default': {
            'level': 'INFO',
            'class': 'django_logging.handlers.DefaultFileHandler',
            'formatter': 'verbose',
            'maxBytes': settings.ROTATE_MB * 1024 * 1024,
            'backupCount': settings.ROTATE_COUNT,
            'filename': '{}/app.log'.format(settings.LOG_PATH)
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'django_logging.handlers.DebugFileHandler',
            'formatter': 'verbose',
            'maxBytes': settings.ROTATE_MB * 1024 * 1024,
            'backupCount': settings.ROTATE_COUNT,
            'filename': '{}/debug.log'.format(settings.LOG_PATH)
        },
        'sql': {
            'level': 'DEBUG',
            'class': 'django_logging.handlers.SQLFileHandler',
            'formatter': 'sql',
            'maxBytes': settings.ROTATE_MB * 1024 * 1024,
            'backupCount': settings.ROTATE_COUNT,
            'filename': '{}/sql.log'.format(settings.LOG_PATH)
        }
    },
    'loggers': {
        'dl_logger': {
            'handlers': LOG_HANDLERS,
            'level': LOG_LEVEL,
            'propagate': True,
        },
    }
}
# Remove handlers that aren't needed so unneeded log files don't get created.
for handler in list(LOGGING['handlers'].keys()):
    if handler not in LOG_HANDLERS:
        del LOGGING['handlers'][handler]
logging.config.dictConfig(LOGGING)


def get_logger():
    logger = logging.getLogger('dl_logger')
    logger.setLevel(LOG_LEVEL)
    return logger
