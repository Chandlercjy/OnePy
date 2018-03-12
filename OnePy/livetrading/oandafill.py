from OnePy.fill.fillbase import FillBase
import arrow


class OandaFill(FillBase):
    def run_fill(self, fillevent):
        """每次指令发过来后，先直接记录下来，然后再去对冲仓位"""
        self.set_dataseries_instrument(fillevent.instrument)
        self._update_info(fillevent)
        # self._update_trade_list(fillevent)
        # self._to_list(fillevent)

    def _update_info(self, fillevent):
        f = self.oanda.get_AccountDetails()["account"]

        instrument = fillevent.instrument
        date = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss")

        inst_info = [i for i in f["positions"] if i["instrument"] in instrument][0]

        position = (float(inst_info["long"]["units"]) - float(inst_info["short"]["units"])) / fillevent.mult  # 注意mult！
        unrealizedPL = float(f["unrealizedPL"])
        realizedPL = float(f["resettablePL"])
        margin = float(f["marginUsed"])
        commission = float(f["commission"])
        balance = float(f["balance"])
        cash = float(f["marginAvailable"])

        self.position.add(date, position)
        self.margin.add(date, margin)
        self.unrealizedPL.add(date, unrealizedPL, unrealizedPL, unrealizedPL)
        self.realizedPL.add(date, realizedPL)
        self.commission.add(date, commission)
        self.cash.add(date, cash)
        self.balance.add(date, balance, balance, balance)

        # 删除重复
        # 第一笔交易会删除update_timeindex产生的初始化信息
        # 第二笔交易开始删除前一笔交易，慢慢迭代，最终剩下最后一笔交易获得的信息
        self.position.del_last()
        # self.avg_price.del_last()
        self.unrealizedPL.del_last()
        self.commission.del_last()
        self.cash.del_last()
        self.balance.del_last()

    def update_timeindex(self, feed_list):
        """
        保持每日收盘后的数据更新
        """
        f = self.oanda.get_AccountDetails()["account"]
        date = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss")

        for feed in feed_list:
            self.set_dataseries_instrument(feed.instrument)

            instrument = feed.instrument

            mult = feed.mult

            inst_info = [i for i in f["positions"] if i["instrument"] in instrument][0]

            position = (float(inst_info["long"]["units"]) - float(inst_info["short"]["units"])) / mult  # 注意mult！
            unrealizedPL = float(f["unrealizedPL"])
            realizedPL = float(f["resettablePL"])
            margin = float(f["marginUsed"])
            commission = float(f["commission"])
            balance = float(f["balance"])
            cash = float(f["marginAvailable"])

            self.position.add(date, position)
            self.margin.add(date, margin)
            self.unrealizedPL.add(date, unrealizedPL, unrealizedPL, unrealizedPL)
            self.realizedPL.add(date, realizedPL)
            self.commission.add(date, commission)
            self.cash.add(date, cash)
            self.balance.add(date, balance, balance, balance)

            # # 检查是否爆仓
            # if self.total_list[-1]["total"] <= 0 or self.cash_list[-1]["cash"] <= 0:
            #     for i in feed_list:
            #         i.continue_backtest = False
            #     print("什么破策略啊都爆仓了！！！！")

    def check_trade_list(self, feed):
        pass

    def check_order_list(self, feed):
        pass
