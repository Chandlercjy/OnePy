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

    def set_basiclevel(self, level=logging.INFO):
        logging.basicConfig(level=level)

    def set_handler(self, name, level):
        self.handler = logging.FileHandler(name)
        self.handler.setLevel(level)

    def set_format(self, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        self.formatter = logging.Formatter(format)

    def addhandler(self):
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


class LiveTradingLogger(LoggerBase):
    def __init__(self):
        super(LiveTradingLogger, self).__init__("Live Trading")
        self.set_handler(arrow.now().format()[:10] + "_Live_Trading.log", logging.WARNING)
        self.set_format('%(name)s - %(message)s')
        self.addhandler()

        self.set_handler(arrow.now().format()[:10] + "_Live_Error.log", logging.ERROR)
        self.set_format('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.addhandler()

class BacktestLogger(LoggerBase):
    def __init__(self):
        super(BacktestLogger, self).__init__("Backtest")
        self.set_handler(arrow.now().format()[:10] + "_Backtest.log", logging.WARNING)
        self.set_format('%(name)s - %(message)s')
        self.addhandler()

        self.set_handler(arrow.now().format()[:10] + "_Backtest_Error.log", logging.ERROR)
        self.set_format('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.addhandler()

