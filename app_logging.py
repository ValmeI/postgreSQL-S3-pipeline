import os
import sys
import traceback
from types import TracebackType
from typing import Optional, Type
from loguru import logger
from config import settings


def check_env_is_aws_lambda() -> bool:
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ


def setup_loguru_logger() -> None:
    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>{exception}"
    )
    is_aws_lambda = check_env_is_aws_lambda()
    # want to keep colorize=True for local development as it makes it easier to read logs
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=log_format,
        colorize=not is_aws_lambda,
        backtrace=True,
        diagnose=True,
    )


def handle_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: Optional[TracebackType],
) -> None:
    """Global exception handler to catch and log any uncaught exceptions:"""
    # Allow program to exit without logging an error when KeyboardInterrupt is raised
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    else:
        traceback_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(
            f"An unhandled exception occurred: {exc_type.__name__}: {exc_value}, traceback: {traceback_string}"
        )


sys.excepthook = handle_exception
setup_loguru_logger()
