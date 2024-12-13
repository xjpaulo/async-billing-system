import logging


def configure_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger


logger = configure_logging()
