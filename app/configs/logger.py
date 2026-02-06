import logging

from app.core.configs import CustomLogger, LogConfig


def get_logger(name="app") -> CustomLogger:
    logging.setLoggerClass(CustomLogger)
    logging.config.dictConfig(LogConfig)
    return logging.getLogger(name)


if __name__ == "__main__":
    logger = get_logger()

    logger.debug("hello world")
    logger.info("ПРИВЕТ МИР!")
    logger.warning("hello world")
    logger.refresh_req_id()

    log = logging.getLogger("nonexist")
    log.refresh_req_id()
    log.debug("hello world")
    log.info("hello world")
    log.warning("hello world")
    log.critical("hello world")

    log2 = logging.getLogger("nonexist2")
    # log2.refresh_req_id()
    log2.debug("hello world")
    log2.info("hello world")
    log2.warning("hello world")
    log2.critical("hello world")

    try:
        logger.error("hello world")
        raise EOFError("EOF!")
    except EOFError:
        logger.critical("CRITICAL MESSAGE", exc_info=True)

    try:
        raise EOFError("EOF!")
    except Exception:
        logger.exception("hello world")
