import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version" : 1,
    "disable_existing_loggers" : False,

    "formatters" : {
        "default" : {
            "format" : "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
    },
    "handlers" : {
        "console" : {
            "class" : "logging.StreamHandler",
            "formatter" : "default",
        },
    },
    "root" : {
        "level" : "INFO",
        "handlers" : ["console"],
    },
}

def setup_logging() -> None:
    dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).info("Logging is configured")

def get_logger(name : str | None = None) -> logging.Logger :
    return logging.getLogger(name or __name__)