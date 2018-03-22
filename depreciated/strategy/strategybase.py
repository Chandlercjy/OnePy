from abc import abstractmethod, ABCMeta
from OnePy.event import events, SignalEvent
from OnePy.indicators.indicator import Indicator
from OnePy.order import BuyOrder, SellOrder, ExitallOrder


class StrategyBase(metaclass=ABCMeta):
    def __init__(self, marketevent):
        self._signal_list = []
        self._mult = marketevent.mult

        self.marketevent = marketevent
        self.instrument = marketevent.instrument

        self.bar = marketevent.bar
        self.bar.set_instrument(self.instrument)
        self.position = marketevent.fill.position
        self.margin = marketevent.fill.margin
        self.avg_price = marketevent.fill.avg_price
        self.unrealizedPL = marketevent.fill.unrealizedPL
        self.realizedPL = marketevent.fill.realizedPL
        self.commission = marketevent.fill.commission
        self.cash = marketevent.fill.cash
        self.balance = marketevent.fill.balance

    def __set_dataseries_instrument(self):
        """确保dataseries对应的instrument为正在交易的品种"""
        self.position.set_instrument(self.instrument)
        self.margin.set_instrument(self.instrument)
        self.avg_price.set_instrument(self.instrument)
        self.unrealizedPL.set_instrument(self.instrument)
        self.realizedPL.set_instrument(self.instrument)
        self.commission.set_instrument(self.instrument)

    def __set_indicator(self):
        """设置技术指标"""
        self.indicator = Indicator(self.marketevent)
        self.i = self.indicator  # alias

    def pips(self, n):
        """
        数值：在price中可正可负，判断是否为挂单。其余只可为正。
        单位：Forex为点数，Futures和Stock为元。
        说明：作为takeprofit、stoploss，trailingstop、price的参数使用，
             实现止盈止损和挂单。
        """
        if self.marketevent.target == "Forex":
            n = n * 1.0 / self._mult * 10
        elif self.marketevent.target in ["Stock", "Futures"]:
            pass
        pips_cls = type("pips", (), dict(pips=n))
        pips_cls.type = "pips"
        return pips_cls

    def pct(self, n):
        """
        数值：在price中可正可负，判断是否为挂单。其余只可为正。
        单位：Forex为点数，Futures和Stock为元。
        说明：作为takeprofit、stoploss，trailingstop、price的参数使用，
             实现止盈止损和挂单。
        示例：若输入1，则为原价格的1%
        """
        n = n * 0.01
        pct_cls = type("pct", (), dict(pct=n))
        pct_cls.type = "pct"
        return pct_cls

    def buy(self, units,
            takeprofit=None,
            stoploss=None,
            trailingstop=None,
            instrument=None,
            price=None):

        buyorder = BuyOrder(self.marketevent)
        buyorder.execute(units=units, price=price, takeprofit=takeprofit,
                         stoploss=stoploss, trailingstop=trailingstop,
                         instrument=instrument)
        self._signal_list.append(SignalEvent(buyorder))

    def sell(self, units,
             takeprofit=None,
             stoploss=None,
             trailingstop=None,
             instrument=None,
             price=None):

        sellorder = SellOrder(self.marketevent)
        sellorder.execute(units=units, price=price, takeprofit=takeprofit,
                          stoploss=stoploss, trailingstop=trailingstop,
                          instrument=instrument)
        self._signal_list.append(SignalEvent(sellorder))

    def exitall(self, instrument=None, price=None):

        exitallorder = ExitallOrder(self.marketevent)

        if self.position[-1] < 0:
            exitallorder.set_ordtype("Buy")
        elif self.position[-1] > 0:
            exitallorder.set_ordtype("Sell")
        elif self.position[-1] == 0:
            exitallorder.set_ordtype("Sell")  # 用来防止其他单触发，一般有Exitall，其他单子就都不触发。
            return

        units = abs(self.position[-1])
        exitallorder.execute(units=units, price=price, takeprofit=None,
                             stoploss=None, trailingstop=None,
                             instrument=instrument)
        self._signal_list.append(SignalEvent(exitallorder))

    def cancel(self):
        pass

    def __start(self):
        self.__set_dataseries_instrument()
        self.__set_indicator()

    def prenext(self):
        pass

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

    def stop(self):
        pass

    def __process(self):
        """
        当数据不够给indicator生成信号时，会产生Warning，无交易发生
        当策略需要更多基本信息，比如10天内的平均仓位，则会产生IndexError，无交易发生，
        会一直更新新行情直到有足够的数据。
        """
        try:
            self.prenext()
            self.next()
        except Warning:
            date = str(self.marketevent.cur_bar.cur_date)
            self._logger.error("No trade on " + date + " for Loading Indicator")

        except IndexError:
            date = str(self.marketevent.cur_bar.cur_date)
            self._logger.error("No trade on " + date + " for Loading other Variables")

    def run_strategy(self):
        self.__start()
        self.__process()
        self.__prestop()
        self.stop()
