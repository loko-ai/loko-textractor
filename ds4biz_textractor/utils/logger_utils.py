import logging


def get_logger():
    logger = logging.getLogger()
    # fhand = logging.FileHandler(fname)
    shand = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # fhand.setFormatter(formatter)
    shand.setFormatter(formatter)

    # logger.addHandler(fhand)
    logger.addHandler(shand)
    logger.setLevel(logging.DEBUG)

    logging.TRACE = 25
    logging.addLevelName(logging.TRACE, 'TRACE')
    setattr(logger, 'trace', lambda message, *args: logger._log(logging.TRACE, message, args))

    logging.PROCESS = 15
    logging.addLevelName(logging.PROCESS, 'PROCESS')
    setattr(logger, 'process', lambda message, *args: logger._log(logging.PROCESS, message, args))

    return logger


logger = get_logger()

if __name__ == '__main__':

    for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
        logger.setLevel(level)
        logger.trace(f"LOG LEVEL :{level}\n")
        logger.debug('msg1')
        logger.info('msg2')
        logger.warning('msg3')
        logger.error('msg4')
        logger.critical('msg5')
        logger.trace('msg6 (custom level)')
        logger.process('msg7 (custom level)\n')
