class Orderdata(object):
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
        self._set_order_info()

    def _set_order_info(self):
        self._set_date()
        self._set_direction()
        self._set_price()
        self._set_takeprofit(self.price)
        self._set_stoploss(self.price)
        self._set_trailingstop()

    def _set_date(self):
        self.date = self._cur_bar.cur_date

    def _set_direction(self):
        if self._ordtype is 'Buy':
            self.direction = 1.0
        elif self._ordtype is 'Sell':
            self.direction = -1.0

    def _set_price(self):
        if self.executemode is 'open':
            self.executemode = self._cur_bar.next_open
        elif self.executemode is 'close':
            self.executemode = self._cur_bar.cur_close

        if self.price in ['open', 'close', None]:  # 判断开盘价还是收盘价成交
            self.price = self.executemode
        elif type(self.price) is type:
            if self.price.type is 'pips':
                self.price = self.price.pips + self.executemode
            elif self.price.type is 'pct':
                self.price = self.executemode * self.price.pct
            else:
                raise SyntaxError('price should be pips or pct!')

    def _set_takeprofit(self, cur_price):
        if self.takeprofit:
            if self.takeprofit.type is 'pips':
                pips = self.takeprofit.pips * self.direction
                self.takeprofit = cur_price + pips
            elif self.takeprofit.type is 'pct':
                pct = 1 + self.takeprofit.pct * self.direction
                self.takeprofit = cur_price * pct
            else:
                raise SyntaxError('takeprofit should be pips or pct!')

    def _set_stoploss(self, cur_price):
        if self.stoploss:
            if self.stoploss.type is 'pips':
                pips = self.stoploss.pips * self.direction
                self.stoploss = cur_price - pips
            elif self.stoploss.type is 'pct':
                pct = 1 - self.stoploss.pct * self.direction
                self.stoploss = cur_price * pct
            else:
                raise SyntaxError('stoploss should be pips or pct!')

    def _set_trailingstop(self):
        if self.trailingstop_pip_pct:
            if self.trailingstop_pip_pct.type is 'pips':
                pips = self.trailingstop_pip_pct.pips * self.direction
                self.trailingstop = self.price - pips
            elif self.trailingstop_pip_pct.type is 'pct':
                pct = 1 - self.trailingstop_pip_pct.pct * self.direction
                self.trailingstop = self.price * pct
            else:
                raise SyntaxError('trailingstop should be pips or pct!')
