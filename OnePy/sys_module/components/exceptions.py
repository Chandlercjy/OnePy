import logging


class BlowUpError(Exception):
    pass


class BacktestFinished(Exception):
    pass


class OrderConflictError(Exception):
    pass


class PctRangeError(Exception):
    pass
