class Orderdata(object):
    """处理order数据，会自动计算好止盈止损移动止损的具体价格"""
    def __init__(self, units, price, takeprofit,
                 stoploss, trailingstop, instrument,
                 cur_bar, executemode, ordtype):
        self.instrument = instrument
        self.units = units
        self.price = price
        self.takeprofit = takeprofit
        self.stoploss = stoploss
        self.trailingstop = trailingstop
        self.trailingstop_pip_pct = trailingstop

        self.executemode = executemode
        self._cur_bar = cur_bar
        self._ordtype = ordtype
        self.__set_order_info()

    def __set_order_info(self):
        """初始化各项数据"""
        self.__set_date()
        self.__set_direction()
        self.__set_price()
        self.__set_takeprofit(self.price)
        self.__set_stoploss(self.price)
        self.__set_trailingstop()

    def __set_date(self):
        """设置时间"""
        self.date = self._cur_bar.cur_date

    def __set_direction(self):
        """设置判断方向"""
        if self._ordtype is "Buy":
            self.direction = 1.0
        elif self._ordtype is "Sell":
            self.direction = -1.0

    def __set_price(self):
        """根据executemode设置价格，并计算最终价格"""
        if self.executemode is "open":
            self.executemode_price = self._cur_bar.next_open
        elif self.executemode is "close":
            self.executemode_price = self._cur_bar.cur_close

        if self.price in ["open", "close", None]:  # 判断开盘价还是收盘价成交
            self.price = self.executemode_price
        elif type(self.price) is type:
            if self.price.type is "pips":
                self.price = self.price.pips + self.executemode_price
            elif self.price.type is "pct":
                self.price = self.executemode_price * self.price.pct
            else:
                raise SyntaxError("price should be pips or pct!")

    def __set_takeprofit(self, cur_price):
        """计算止盈价格"""
        if self.takeprofit:
            if self.takeprofit.type is "pips":
                if self.takeprofit.pips < 0:
                    raise SyntaxError("pips in takeprofit should be positive!")
                pips = self.takeprofit.pips * self.direction
                self.takeprofit = cur_price + pips
            elif self.takeprofit.type is "pct":
                if self.takeprofit.pct < 0:
                    raise SyntaxError("pips in takeprofit should be positive!")
                pct = 1 + self.takeprofit.pct * self.direction
                self.takeprofit = cur_price * pct
            else:
                raise SyntaxError("takeprofit should be pips or pct!")

    def __set_stoploss(self, cur_price):
        """计算止损价格"""
        if self.stoploss:
            if self.stoploss.type is "pips":
                if self.stoploss.pips < 0:
                    raise SyntaxError("pips in stoploss should be positive!")
                pips = self.stoploss.pips * self.direction
                self.stoploss = cur_price - pips
            elif self.stoploss.type is "pct":
                if self.stoploss.pct < 0:
                    raise SyntaxError("pct in stoploss should be positive!")
                pct = 1 - self.stoploss.pct * self.direction
                self.stoploss = cur_price * pct
            else:
                raise SyntaxError("stoploss should be pips or pct!")

    def __set_trailingstop(self):
        """计算追踪止损价格"""
        if self.trailingstop_pip_pct:
            if self.trailingstop_pip_pct.type is "pips":
                if self.trailingstop_pip_pct.pips < 0:
                    raise SyntaxError("pips in trailingstop should be positive!")
                pips = self.trailingstop_pip_pct.pips * self.direction
                self.trailingstop = self.price - pips
            elif self.trailingstop_pip_pct.type is "pct":
                if self.trailingstop_pip_pct.pct < 0:
                    raise SyntaxError("pct in trailingstop should be positive!")
                pct = 1 - self.trailingstop_pip_pct.pct * self.direction
                self.trailingstop = self.price * pct
            else:
                raise SyntaxError("trailingstop should be pips or pct!")
