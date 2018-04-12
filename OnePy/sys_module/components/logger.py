
import logging

import arrow


class LoggerBase():
    """
    CRITICAL	50
    ERROR	40
    WARNING	30
    INFO	20
    DEBUG	10
    NOTSET	0
    """

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.formatter = None
        self.handler = None

    def _set_handler(self, name, level):
        self.handler = logging.FileHandler(name)
        self.handler.setLevel(level)

    def _set_format(self, formatter):
        self.formatter = logging.Formatter(formatter)

    def _addhandler(self):
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def set_info(self, file=True):
        if file:
            self._save_to_file()
        logging.basicConfig(level=logging.INFO)

    def set_debug(self, file=True):
        if file:
            self._save_to_file()
        logging.basicConfig(level=logging.DEBUG)

    def set_warning(self, file=True):
        if file:
            self._save_to_file()
        logging.basicConfig(level=logging.WARNING)

    def set_error(self, file=True):
        if file:
            self._save_to_file()
        logging.basicConfig(level=logging.ERROR)

    def set_critical(self, file=True):
        if file:
            self._save_to_file()
        logging.basicConfig(level=logging.CRITICAL)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


class BacktestLogger(LoggerBase):
    def __init__(self):
        super(BacktestLogger, self).__init__("Backtest")

    def _save_to_file(self):
        self._set_handler(arrow.now().format(
            "YYYY-MM-DD")+'.log', logging.INFO)
        self._set_format('%(name)s - %(message)s')
        self._addhandler()

        self._set_handler(arrow.now().format(
            "YYYY-MM-DD")+'_warning.log', logging.WARNING)
        self._set_format(
            '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s  %(message)s')
        self._addhandler()
