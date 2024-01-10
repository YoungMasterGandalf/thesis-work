import os
import logging
import colorlog
from pythonjsonlogger import jsonlogger

from logging.handlers import RotatingFileHandler

LOG_FILE_PATH: str = "/nfshome/chmurnyd/datacube_logs.json"
MAX_BYTES_LIMIT: int = 5 * 10**6 # Maximum amount of bytes the .json file will store --> then it will be archived/deleted
BACKUP_COUNT: int = 1 # Maximum number of archived log files

def create_logger_name_from_python_file_path(python_file_path: str) -> str:
    file_name = os.path.basename(python_file_path)
    logger_name = file_name.replace(".py", "")
    
    return logger_name

def setup_logger(logger_name: str):
    # Create a logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create a JSON formatter --> will be used for formatting of logs into json file
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(name)s %(asctime)s %(levelname)s %(filename)s %(lineno)s %(process)d %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%SZ',
        rename_fields={"levelname": "severity", "asctime": "timestamp"}
    )

    # Create a formatter --> will be used for formatting of logs into sys.stdout
    log_formatter = colorlog.ColoredFormatter(
        "%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(blue)s%(filename)s:%(lineno)s%(reset)s | %(process)d >>> %(log_color)s%(message)s%(reset)s",
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )

    # Create a file handler
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=MAX_BYTES_LIMIT, backupCount=BACKUP_COUNT)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    # Create a stream handler (for console output)
    stream_handler = colorlog.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Adjust level as needed
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger

if __name__ == "__main__":
    # Example usage
    logger = setup_logger()

    # Example log statements
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
