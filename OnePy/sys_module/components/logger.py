
import logging


class LoggerFactory:

    """
    CRITICAL	50
    ERROR	40
    WARNING	30
    INFO	20
    DEBUG	10
    NOTSET	0
    """

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger_name = logger_name

        self.settle_info()
        self.settle_warning()

    def _set_file(self, logger_name, level_name, level, log_format):
        file_handler = logging.FileHandler(f'{logger_name}_{level_name}.log')

        formatter = logging.Formatter(log_format)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def settle_info(self):
        self._set_file(self.logger_name, "INFO", logging.INFO, '%(message)s')

    def settle_warning(self):
        self._set_file(self.logger_name, "WARNING", logging.WARNING,
                       '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
