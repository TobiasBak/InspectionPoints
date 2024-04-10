import logging

from constants import recurring_level, non_recurring_level, recurring_filename, non_recurring_filename


def get_recurring_logger(name: str):
    return _get_logger(name, recurring_filename, recurring_level, "recurring")


def get_non_recurring_logger(name: str):
    return _get_logger(name, non_recurring_filename, non_recurring_level, "non_recurring")


def _get_logger(name: str, filename: str, level: int, extension_name: str) -> logging.Logger:
    logger = logging.getLogger(f"{name}; ({extension_name})")
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s %(msecs)03dms - %(name)s %(levelname)s: %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # like the console handler, create the file handler
    # This should log all levels
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger.addHandler(fh)


    # log to csv
    # create csv handler
    split_name = filename.split(".")[0]
    csv_handler = logging.FileHandler(split_name + ".csv")
    csv_handler.setLevel(logging.DEBUG)
    csv_handler.setFormatter(logging.Formatter('%(asctime)s %(msecs)03d;%(name)s;%(levelname)s;%(message)s',
                                               datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(csv_handler)

    return logger
