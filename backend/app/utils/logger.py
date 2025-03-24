from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("logs/app.log", rotation="500 MB", retention="10 days", level="DEBUG")

def log_event(event: str, level: str = "INFO"):
    if level == "INFO":
        logger.info(event)
    elif level == "WARNING":
        logger.warning(event)
    elif level == "ERROR":
        logger.error(event)
    else:
        logger.debug(event)