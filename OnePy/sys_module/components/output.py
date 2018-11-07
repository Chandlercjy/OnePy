import pandas as pd

from OnePy.builtin_module.plotters.by_matplotlib import Matplotlib
from OnePy.builtin_module.plotters.by_plotly import Plotly
from OnePy.custom_module.analysis import (AmazingAnalysis, get_max_drawdown,
                                          get_max_drawdown_date,
                                          get_max_duration_in_drawdown,
                                          get_sharpe_ratio)
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.utils.awesome_func import dict_to_table
from OnePy.utils.easy_func import check_setting


class OutPut(OnePyEnvBase):

    def show_setting(self, check_only: bool = False):
        show_list = [(self.env.readers, 'readers'),
                     (self.env.cleaners, 'cleaners'),
                     (self.env.strategies, 'strategy'),
                     (self.env.brokers, 'brokers'),
                     (self.env.risk_managers, 'risk_managers'),
                     (self.env.recorders, 'recorders')]
        [check_setting(show, name, check_only) for show, name in show_list]

    def summary(self):
        """在最后输出简要回测结果"""
        d = {}

        balance = self.env.recorder.balance.dataframe()
        daily_basis_balance = balance.resample('D').last().dropna()
        initial_balance = balance.values[0][0]
        end_balance = balance.values[-1][0]
        total_return = end_balance / initial_balance - 1
        max_drawdown = get_max_drawdown(balance)
        max_drawdown_date = get_max_drawdown_date(balance)
        max_duration_in_drawdown = get_max_duration_in_drawdown(
            daily_basis_balance)
        sharpe_ratio = get_sharpe_ratio(daily_basis_balance)

        d["Fromdate"] = self.env.fromdate
        d["Todate"] = self.env.todate
        d["Initial_Value"] = f'${initial_balance:.2f}'
        d["Final_Value"] = f'${end_balance:.2f}'
        d["Total_Return"] = f'{total_return*100:.3f}%'
        d["Max_Drawdown"] = f'{max_drawdown*100:.3f}%'
        d["Max_Duration"] = f'{max_duration_in_drawdown} days'
        d["Max_Drawdown_Date"] = f'{max_drawdown_date}'
        d["Sharpe_Ratio"] = f'{sharpe_ratio:.2f}'
        dict_to_table(d)

    def save_result(self, name):
        result = {}
        result['balance'] = self.env.recorder.balance.dataframe()
        result['cash'] = self.env.recorder.cash.dataframe()
        result['position'] = self.env.recorder.position.dataframe()
        result['holding_pnl'] = self.env.recorder.holding_pnl.dataframe()
        result['commission'] = self.env.recorder.commission.dataframe()
        result['market_value'] = self.env.recorder.market_value.dataframe()
        result['margin'] = self.env.recorder.margin.dataframe()
        result['detail_summary'] = self.analysis.detail_summary()
        result['general_summary'] = self.analysis.general_summary()
        result['trade_log'] = self.trade_log()
        pd.to_pickle(result, name)

    @property
    def analysis(self) -> AmazingAnalysis:
        return AmazingAnalysis()

    @staticmethod
    def plot(ticker: str, engine: str='matplotlib'):
        if engine == 'matplotlib':
            Matplotlib().plot(ticker)
        else:
            Plotly().plot(ticker)

    @staticmethod
    def trade_log() -> pd.DataFrame:
        return AmazingAnalysis().get_full_trade_log()

    @staticmethod
    def summary2():
        analysis = AmazingAnalysis()
        dict_to_table(analysis.general_summary())
        print(analysis.detail_summary())
