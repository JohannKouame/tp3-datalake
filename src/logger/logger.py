import logging
import os
import sys

from pythonjsonlogger import jsonlogger


class Logger:
    def __init__(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG if os.getenv('DEBUG_MODE') == "2" else logging.INFO)
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter("%(asctime)%(message)%(levelname)")
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
