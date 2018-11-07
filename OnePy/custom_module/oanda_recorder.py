import arrow

from oandakey import access_token, accountID
from OnePy.builtin_module.backtest_forex.forex_recorder import ForexRecorder
from OnePy.custom_module.api.oanda_api import OandaAPI
from OnePy.custom_module.oanda_bar import OandaBar
from OnePy.sys_module.models.base_series import (AvgPriceSeries, MoneySeries,
                                                 PositionSeries)


class OandaRecorder(ForexRecorder):
    def __init__(self):
        super().__init__()
        self.oanda = OandaAPI(accountID, access_token)

    def initialize(self):

        self.settle_match_engine_and_series()
        self.holding_pnl = self.series.HoldingPnlSeries(250)
        self.realized_pnl = self.series.RealizedPnlSeries(250)
        self.commission = self.series.CommissionSeries(250)
        self.market_value = self.series.MarketValueSeries(250)
        self.margin = self.series.MarginSeries(250)  # 无法更新，没有分别提供long，short信息

        self.position = PositionSeries(250)
        self.avg_price = AvgPriceSeries(250)

        self.cash = MoneySeries("cash", self.initial_cash, 250)
        self.frozen_cash = MoneySeries("frozen_cash", 0, 250)
        self.balance = MoneySeries("balance", self.initial_cash, 250)

        account_details = self.oanda.get_AccountDetails()
        account = account_details["account"]
        positions = account["positions"]

        for position in positions:
            ticker = position["instrument"]

            if ticker in self.env.tickers:
                for long_or_short in ["long", "short"]:
                    info = position[long_or_short]
                    self.position.change_initial_value(
                        ticker, abs(float(info["units"])), long_or_short
                    )

                    self.holding_pnl.change_initial_value(
                        ticker, float(info["unrealizedPL"]), long_or_short
                    )
                    self.commission.change_initial_value(
                        ticker, float(position["commission"]), long_or_short
                    )

                    if info.get("averagePrice"):
                        self.avg_price.change_initial_value(
                            ticker, float(info["averagePrice"]), long_or_short
                        )
                    else:
                        self.avg_price.change_initial_value(ticker, 0, long_or_short)

        self.cash.change_initial_value(float(account["marginAvailable"]))
        self.balance.change_initial_value(float(account["NAV"]))
        self.frozen_cash.change_initial_value(float(account["marginUsed"]))

    def set_setting(self, slippage: dict, margin_rate=0.02) -> None:
        self.slippage = slippage
        self.margin_rate = margin_rate

    def run(self):
        # self._record_order()
        pass

    def update(self, order_executed=False):
        """取消了margin,market_value,"""

        trading_date = arrow.now().format("YYYY-MM-DD HH:mm:ss")

        account_details = self.oanda.get_AccountDetails()
        account = account_details["account"]
        positions = account["positions"]

        for position in positions:
            ticker = position["instrument"]

            if ticker in self.env.tickers:
                for long_or_short in ["long", "short"]:
                    info = position[long_or_short]
                    self.position._append_value(
                        ticker, abs(float(info["units"])), long_or_short
                    )
                    self.holding_pnl._append_value(
                        ticker, float(info["unrealizedPL"]), long_or_short
                    )
                    self.commission._append_value(
                        ticker, float(position["commission"]), long_or_short
                    )

                    if info.get("averagePrice"):
                        self.avg_price.change_initial_value(
                            ticker, float(info["averagePrice"]), long_or_short
                        )
                    else:
                        self.avg_price.change_initial_value(ticker, 0, long_or_short)

        self.cash.append(
            {"date": trading_date, "value": float(account["marginAvailable"])}
        )
        self.balance.append({"date": trading_date, "value": float(account["NAV"])})
        self.frozen_cash.append(
            {"date": trading_date, "value": float(account["marginUsed"])}
        )

        self.market_value.update_barly(False)
        self.margin.update_barly()

    def none(self):

        if not order_executed:
            positions = self.oanda.get_AccountDetails()["account"]["positions"][0]

            true_holing_pnl = (
                self.holding_pnl.total_value() - self.commission.total_value()
            )
            print("=" * 30)
            print("balance", self.balance.latest())
            print("size", self.position.total_value(), positions["long"]["units"])
            print("margin", self.margin.total_value(), positions["marginUsed"])
            print("cash", self.cash.latest())
            print(
                "holding_pnl",
                self.holding_pnl.total_value(),
                positions["long"]["unrealizedPL"],
            )
            print("true holding_pnl", true_holing_pnl)
            print("commission", self.commission.total_value(), positions["commission"])
            print("market_value", self.market_value.total_value())

            try:
                print(
                    "avgPrice",
                    self.avg_price.latest("EUR_USD", "long"),
                    positions["long"]["averagePrice"],
                )
            except:
                print("no position")

    @property
    def bar_class(self):
        return OandaBar
