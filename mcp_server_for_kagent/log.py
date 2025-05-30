import logging.config
from os import getenv

default_logging_level = "INFO"


def setup_logging():
    level = getenv("LOGGING_LEVEL", default_logging_level).upper()

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "standard": {
                    "format": "[%(asctime)s | %(levelname)s | %(funcName)s]: %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "level": level,
                    "formatter": "standard",
                },
            },
            "root": {
                "handlers": ["stdout"],
                "level": level,
            },
        }
    )
