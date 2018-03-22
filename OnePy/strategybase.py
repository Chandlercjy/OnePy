

class StrategyBase(metaclass=ABCMeta):
    def __init__(self, marketevent):
        self._signal_list = []
        self.g = Global  # TODO：总的global 类
        self.context = self.g.context

    def __set_dataseries_instrument(self):
        """确保dataseries对应的instrument为正在交易的品种"""
        pass

    def __set_indicator(self):
        """设置技术指标"""
        self.indicator = Indicator(self.marketevent)
        self.i = self.indicator  # alias
    def __start(self):
        self.__set_dataseries_instrument()
        self.__set_indicator()

    @abstractmethod
    def next(self):
        """这里写主要的策略思路,必须在子类中被override"""
        raise NotImplementedError("next should be overridden")

    def __prestop(self):
        """检查，若做多做空和一键平仓同时出现，则只一键平仓"""

        for i in self._signal_list:
            if i.exectype == "CloseAll":
                self._signal_list = [] if i.units == 0 else [i]

                break

        for i in self._signal_list:
            if i.instrument is self.instrument:
                events.put(i)

    def __process(self):
        """
        当数据不够给indicator生成信号时，会产生Warning，无交易发生
        当策略需要更多基本信息，比如10天内的平均仓位，则会产生IndexError，无交易发生，
        会一直更新新行情直到有足够的数据。
        """
        try:
            self.next()
        except Warning:
            date = str(self.marketevent.cur_bar.cur_date)
            self._logger.error("No trade on " + date +
                               " for Loading Indicator")

        except IndexError:
            date = str(self.marketevent.cur_bar.cur_date)
            self._logger.error("No trade on " + date +
                               " for Loading other Variables")

    def run_strategy(self):
        self.__start()
        self.__process()
        self.__prestop()


class OrderExecutor(object):

    """存储可以执行的信号类型"""

    def __init__(self):
        pass

    def buy(self):  # Market Order
        pass

    def sell(self):  # Market Order
        pass

    def short_sell(self):
        pass

    def short_cover(self):
        pass

    def exit_all(self):
        pass

    def cancel_all(self):
        pass

class OrderInfo(object):

    """存储Order的信息"""

    def __init__(self, units, takeprofit, stoploss, trailingstop, ticker, price):
        """TODO: to be defined1.

        :units: TODO
        :takeprofit: TODO
        :stoploss: TODO
        :trailingstop: TODO
        :ticker: TODO
        :price: TODO

        """
        self._units = units
        self._takeprofit = takeprofit
        self._stoploss = stoploss
        self._trailingstop = trailingstop
        self._ticker = ticker
        self._price = price


class OrderType(object):

    LIMIT_SELL = 'limit_sell'

    LIMIT_BUY = 'limit_buy'

    STOP_SELL = 'stop_sell'

    STOP_BUY = 'stop_buy'

    TRAILING_STOP_BUY = 'trailing_stop_buy'

    TRAILING_STOP_SELL = 'trailing_stop_sell'
