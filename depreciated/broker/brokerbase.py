from abc import abstractmethod, ABCMeta


class BrokerBase(metaclass=ABCMeta):
    def __init__(self):
        self.fill = None
        self._notify_onoff = False
        self.orderevent = None

    def _set_logger(self, logger):
        self._logger = logger

    @abstractmethod
    def submit_order(self):
        raise NotImplementedError("submit_order shold be overrided")

    @abstractmethod
    def notify(self):
        raise NotImplementedError("notify shold be overrided")

    @abstractmethod
    def change_status(self):
        raise NotImplementedError("change_status shold be overrided")

    @abstractmethod
    def start(self):
        raise NotImplementedError("start shold be overrided")

    @abstractmethod
    def prenext(self):
        raise NotImplementedError("prenext shold be overrided")

    @abstractmethod
    def next(self):
        raise NotImplementedError("next shold be overrided")

    @abstractmethod
    def check_before(self):
        raise NotImplementedError("check_before shold be overrided")

    @abstractmethod
    def check_after(self):
        raise NotImplementedError("check_after shold be overrided")

    def run_broker(self, orderevent):
        self.orderevent = orderevent
        self.start()
        self.prenext()
        self.next()
