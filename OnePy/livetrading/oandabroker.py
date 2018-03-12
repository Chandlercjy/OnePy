import arrow

from OnePy.broker.brokerbase import BrokerBase
from OnePy.event import events, LiveFillEvent


class OandaBroker(BrokerBase):
    def __init__(self):
        super(OandaBroker, self).__init__()

        self.fillevent_checked = None
        self._notify_onoff = False

        self.oanda = None  # will be settled in OnePiece

    def submit_order(self):
        """发送交易指令"""
        fillevent = LiveFillEvent(self.orderevent.order)
        events.put(fillevent)

        info = dict(instrument=self.orderevent.instrument,
                    units=self.orderevent.units * self.orderevent.mult * self.orderevent.direction)

        info["takeprofit"] = self.orderevent.takeprofit
        info["stoploss"] = self.orderevent.stoploss
        info["trailingstop"] = self.orderevent.trailingstop

        if self.orderevent.exectype in ["StopOrder", "LimitOrder"]:
            info["price"] = self.orderevent.price
            info["requesttype"] = self.orderevent.exectype
            self.status, self.exectype = self.oanda.OrderCreate_pending(**info), info["requesttype"]
        elif self.orderevent.exectype is "CloseAll":
            if self.orderevent.ordtype is "Buy":
                status = self.oanda.close_all_position(instrument=self.orderevent.instrument,
                                                       closetype="short")
            elif self.orderevent.ordtype is "Sell":
                status = self.oanda.close_all_position(self.orderevent.instrument,
                                                       closetype="long")
            self.status, self.exectype = status, "CloseAll"

        else:
            self.status, self.exectype = self.oanda.OrderCreate_mkt(**info), "MarketOrder"

    def check_after(self):
        """检查Order发送后是否执行成功"""
        return True

    def start(self):
        self.notify()
        self.submit_order()
        self.notify2()

    def prenext(self):
        pass

    def next(self):
        info = self.oanda.get_AccountDetails()
        info["instrument"] = self.orderevent.instrument
        events.put(LiveFillEvent(self.orderevent.order))

    def notify(self):
        self._logger.warning("{d}, {i}, {s} {st} @ {p}, units: {si}, Execute: {ot}\
        ".format(d=self.orderevent.date,
                 i=self.orderevent.instrument,
                 s=self.orderevent.ordtype,
                 st=self.orderevent.status,
                 p=self.orderevent.price,
                 si=self.orderevent.units,
                 ot=self.orderevent.exectype))

    def notify2(self):
        s = self.status
        if s.get("orderCreateTransaction"):
            so = s["orderCreateTransaction"]
            d = arrow.get(so["time"]).format("YYYY-MM-DD HH:mm:ss")
            i = so["instrument"]
            si = float(so["units"]) * self.orderevent.direction
            sd = so["type"]
            st = "Submitted"
            bs = self.orderevent.ordtype

            if so.get("price"):
                p = so["price"]
            else:
                p = "Checking"

            self._logger.warning(f"{d}, {i}, {bs} {st} @ {p}, units: {si}, Execute: {sd}")
        if s.get("orderFillTransaction"):
            sf = s["orderFillTransaction"]
            sd = sf["type"]
            p = sf["price"]
            st = "Filled"
            co = sf["commission"]
            self._logger.warning(f"{d}, {i}, {bs} {st} @ {p}, units: {si}, Execute: {sd}, Comm: {co}")

    def change_status(self):
        pass

    def check_before(self):
        pass

    def check_after(self):
        pass


if __name__ == '__main__':
    import logging
    from OnePy.livetrading import oanda
    from oandakey import access_token, accountID
    from OnePy.logger import BacktestLogger

    logging.basicConfig(level=logging.WARNING)

    simu_order = type("simulate", (), {})
    orderevent = simu_order()
    orderevent.order = None
    orderevent.date = "2017-01-01"
    orderevent.mult = 100000
    orderevent.status = "Created"

    # 修改
    orderevent.instrument = "EUR_USD"
    orderevent.ordtype = "Buy"  # Buy, Sell
    orderevent.exectype = "StopOrder"  # MarketOrder, StopOrder, LimitOrder, CloseAll
    orderevent.units = 0.01
    orderevent.price = 1.20
    orderevent.takeprofit = None
    orderevent.stoploss = None
    orderevent.trailingstop = None

    orderevent.direction = 1 if orderevent.ordtype == "Buy" else -1

    broker = OandaBroker()
    broker.oanda = oanda.oanda_api(accountID, access_token)

    broker._logger = BacktestLogger()
    broker.order = None

    broker.run_broker(orderevent)
