import matplotlib.pyplot as plt
import matplotlib.style as style
import statsmodels.api as sm
from matplotlib.widgets import MultiCursor

import OnePy.custom_module.analysis as analysis
from OnePy.builtin_module.plotters.by_plotly import PlotBase


class Matplotlib(PlotBase):

    def setting(self):
        style.use('ggplot')
        plt.rcParams['lines.linewidth'] = 1.4
        plt.rcParams['figure.figsize'] = 6, 10

    def close_df(self, ticker):
        dataframe = self.ohlc_df(ticker)[['close']]
        dataframe.rename(columns=dict(close=ticker), inplace=True)

        return dataframe

    def plot(self, ticker):
        self.setting()

        fig = plt.figure(tight_layout=True)
        ax1 = fig.add_subplot(5, 2, 1)
        ax2 = fig.add_subplot(5, 2, 2)
        ax3 = fig.add_subplot(5, 2, 3)
        ax4 = fig.add_subplot(5, 2, 4)
        ax5 = fig.add_subplot(5, 2, 5)
        ax6 = fig.add_subplot(5, 2, 6)
        ax7 = fig.add_subplot(5, 2, 7)
        ax8 = fig.add_subplot(5, 2, 8)
        ax9 = fig.add_subplot(5, 2, 9)
        ax10 = fig.add_subplot(5, 2, 10)

        # 左边
        self.close_df(ticker).plot(ax=ax1, sharex=ax5)

        self.balance_df.plot(ax=ax3)
        self.cash_df.plot(ax=ax5, sharex=ax5)
        analysis.get_drawdown_df(self.balance_df).plot(ax=ax9, sharex=ax5)

        holding_pnl = self.env.recorder.holding_pnl.single_dataframe()

        holding_pnl.rename(columns=dict(
            value=f'holding_pnl'), inplace=True)
        holding_pnl.plot(ax=ax7, sharex=ax5)
        # for i in self.holding_pnl_df:
        # i.plot(ax=ax7, sharex=ax5)

        # 右边

        market_value = self.env.recorder.market_value.single_dataframe()

        market_value.rename(columns=dict(
            value=f'market_value'), inplace=True)
        market_value.plot(ax=ax2, sharex=ax5)

        margin = self.env.recorder.margin.single_dataframe()

        margin.rename(columns=dict(
            value=f'margin'), inplace=True)
        margin.plot(ax=ax4, sharex=ax5)

        # for i in self.positions_df:
        # i.plot(ax=ax2, sharex=ax5)

        # for i in self.margin_df:
        # i.plot(ax=ax4, sharex=ax5)

        self.realized_pnl_df.plot(ax=ax6, sharex=ax5, kind='bar')

        sm.qqplot(self.returns_df['returns'],
                  dist='norm', line='s', ax=ax8, marker='.')
        self.returns_df[self.returns_df != 0].hist(bins=100, ax=ax10)

        MultiCursor(fig.canvas, (ax1, ax2, ax3, ax4, ax5, ax6,
                                 ax7,  ax9), color='r', lw=1)
        plt.show()

    def plot_A_share(self, ticker):
        self.setting()

        fig = plt.figure(tight_layout=True)
        ax1 = fig.add_subplot(5, 2, 1)
        ax2 = fig.add_subplot(5, 2, 2)
        ax3 = fig.add_subplot(5, 2, 3)
        ax4 = fig.add_subplot(5, 2, 4)
        ax5 = fig.add_subplot(5, 2, 5)
        ax6 = fig.add_subplot(5, 2, 6)
        ax7 = fig.add_subplot(5, 2, 7)
        ax8 = fig.add_subplot(5, 2, 8)
        ax9 = fig.add_subplot(5, 2, 9)
        ax10 = fig.add_subplot(5, 2, 10)

        # 左边
        self.close_df(ticker).plot(ax=ax1, sharex=ax5)

        self.balance_df.plot(ax=ax3)
        self.cash_df.plot(ax=ax5, sharex=ax5)
        analysis.get_drawdown_df(self.balance_df).plot(ax=ax9, sharex=ax5)

        holding_pnl = self.env.recorder.holding_pnl.single_dataframe()

        holding_pnl.rename(columns=dict(
            value=f'holding_pnl'), inplace=True)
        holding_pnl.plot(ax=ax7, sharex=ax5)
        # for i in self.holding_pnl_df:
        # i.plot(ax=ax7, sharex=ax5)

        # 右边

        market_value = self.env.recorder.market_value.single_dataframe()

        market_value.rename(columns=dict(
            value=f'market_value'), inplace=True)
        market_value.plot(ax=ax2, sharex=ax5)

        margin = self.env.recorder.margin.single_dataframe()

        margin.rename(columns=dict(
            value=f'margin'), inplace=True)
        margin.plot(ax=ax4, sharex=ax5)

        # for i in self.positions_df:
        # i.plot(ax=ax2, sharex=ax5)

        # for i in self.margin_df:
        # i.plot(ax=ax4, sharex=ax5)

        self.realized_pnl_df.plot(ax=ax6, sharex=ax5, kind='bar')

        sm.qqplot(self.returns_df['returns'],
                  dist='norm', line='s', ax=ax8, marker='.')
        self.returns_df[self.returns_df != 0].hist(bins=100, ax=ax10)

        MultiCursor(fig.canvas, (ax1, ax2, ax3, ax4, ax5, ax6,
                                 ax7,  ax9), color='r', lw=1)
        plt.show()
