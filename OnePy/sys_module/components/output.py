import pandas as pd

from OnePy.builtin_module.plotters.by_plotly import Plotly
from OnePy.environment import Environment
from OnePy.utils.easy_func import check_setting
from OnePy.utils.statistics import create_drawdowns, create_sharpe_ratio, stats


class OutPut(object):
    env = Environment

    @classmethod
    def show_setting(self, check_only=False):
        show_list = [(self.env.readers, 'readers'),
                     (self.env.cleaners, 'cleaners'),
                     (self.env.strategies, 'strategy'),
                     (self.env.brokers, 'brokers'),
                     (self.env.risk_managers, 'risk_managers'),
                     (self.env.recorders, 'recorders')]
        [check_setting(show, name, check_only) for show, name in show_list]

    @classmethod
    def summary(self):
        """在最后输出简要回测结果"""
        total = pd.DataFrame(list(self.env.recorder.balance))
        total.set_index("date", inplace=True)
        pct_returns = total.pct_change()
        total = total / self.env.recorder.initial_cash
        max_drawdown, duration = create_drawdowns(total["value"])
        initial_cash = self.env.recorder.initial_cash
        final_value = self.env.recorder.balance.latest()
        sharpe_ratio = create_sharpe_ratio(pct_returns, len(pct_returns))
        d = {}
        d["Final_Value"] = f'${final_value:.2f}'
        d["Total_return"] = f'{(final_value/initial_cash-1)*100:.5f}%'
        d["Max_Drawdown"], d["Duration"] = f'{max_drawdown*100:.5f}%', duration
        d["Sharpe_Ratio"] = f'{sharpe_ratio:.5f}'
        print(dict_to_table(d))

    @classmethod
    def all_dataframe(self):
        recorder = self.env.recorder
        cash = recorder.cash.dataframe()
        balance = recorder.balance.dataframe()
        frozen_cash = recorder.frozen_cash.dataframe()
        position = recorder.position.dataframe()
        avg_price = recorder.avg_price.dataframe()
        holding_pnl = recorder.holding_pnl.dataframe()
        realized_pnl = recorder.realized_pnl.dataframe()
        commission = recorder.commission.dataframe()
        market_value = recorder.market_value.dataframe()
        margin = recorder.margin.dataframe()

        dataframe = pd.concat([cash, balance, frozen_cash, position, avg_price,
                               holding_pnl, realized_pnl, commission, market_value, margin], axis=1)

        dataframe.fillna(method='ffill', inplace=True)

        return dataframe

    @classmethod
    def plot(self, ticker):
        plotter = Plotly()

        return plotter.plot(ticker)
