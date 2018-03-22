from .strategybase import StrategyBase


class MyStrategy(StrategyBase):

    def prenext(self):
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.i.SMA(period=30, index=-1) > self.i.SMA(period=50, index=-1):
            if self.unrealizedPL[-1] <= 0:
                self.buy(0.1, takeprofit=self.pips(200),  # 设置止盈为200个pips，不可为负
                         stoploss=self.pct(1),  # 设置止损为成交价的1%，不可为负
                         trailingstop=self.pips(60))  # 设置追踪止损，盈利时触发
        else:
            self.sell(0.05, price=self.pips(50),  # 设置挂单，默认为第二天open价格加50点，也可为负数
                      takeprofit=self.pips(200),
                      stoploss=self.pips(200),
                      trailingstop=self.pips(60))

            if self.unrealizedPL[-2] > self.unrealizedPL[-1] and self.unrealizedPL[-2] > 100:
                self.exitall()  # 设置浮亏浮盈大于100元且出现下降时清仓

class Buy_and_hold(StrategyBase):
    def prenext(self):
        pass

    def next(self):
        self.buy(0.1)