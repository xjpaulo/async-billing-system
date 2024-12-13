import logging

from app.utils.logger import configure_logging


def test_configure_logging():
    logger = configure_logging()
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
