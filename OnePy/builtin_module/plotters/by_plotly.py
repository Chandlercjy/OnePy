
import pandas as pd
from plotly import graph_objs as go
from plotly import offline as py

from OnePy.sys_module.metabase_env import OnePyEnvBase


class PlotBase(OnePyEnvBase):

    def __init__(self):
        super().__init__()
        self.balance_df = self.env.recorder.balance.dataframe()
        self.cash_df = self.env.recorder.cash.dataframe()
        self.positions_df = self.env.recorder.position.dataframe()
        self.holding_pnl_df = self.env.recorder.holding_pnl.dataframe()
        self.commission_df = self.env.recorder.commission.dataframe()
        self.margin_df = self.env.recorder.margin.dataframe()
        self.data = []
        self.updatemenus = []

    @property
    def realized_pnl_df(self):
        trade_log = self.env.recorder.match_engine.generate_trade_log()
        trade_log.dropna(inplace=True)
        df = trade_log[['exit_date', 're_pnl']].copy()
        df.rename(columns=dict(exit_date='date'), inplace=True)
        df.set_index('date', drop=True, inplace=True)
        df.index = pd.to_datetime(df.index)

        return df

    def ohlc_df(self, ticker):
        ohlc = self.env.readers[ticker].load(
            self.env.fromdate, self.env.todate)
        dataframe = pd.DataFrame((i for i in ohlc))
        dataframe.set_index('date', inplace=True)
        dataframe.index = pd.to_datetime(dataframe.index)

        return dataframe


class Plotly(PlotBase):

    def plot(self, instrument=None, engine='plotly', notebook=False):

        if engine == 'plotly':
            if isinstance(instrument, str):
                df = self.ohlc_df(instrument)
                p_symbol = go.Scatter(x=df.index, y=df.close,
                                      xaxis='x3', yaxis='y3', name=instrument)
                p_volume = go.Bar(x=df.index, y=df['volume'],
                                  xaxis='x3', yaxis='y5', opacity=0.5, name='volume')
                self.data.append(p_symbol)
                self.data.append(p_volume)

            if isinstance(instrument, list):
                for i in instrument:
                    df = self.ohlc_df(instrument)
                    p_symbol = go.Scatter(x=df.index, y=df.close,
                                          xaxis='x3', yaxis='y3', name=i)
                    p_volume = go.Bar(x=df.index, y=df['volume'],
                                      xaxis='x3', yaxis='y5',
                                      opacity=0.5, name=i + 'volume')
                    self.data.append(p_symbol)
                    self.data.append(p_volume)

        for i in self.positions_df:
            self.positions_df.sort_index(inplace=True)
            p_position = go.Scatter(x=self.positions_df.index,
                                    y=self.positions_df[i],
                                    xaxis='x2', yaxis='y2', name=i)
            self.data.append(p_position)

        for i in self.realized_pnl_df:
            self.realized_pnl_df.sort_index(inplace=True)
            p_re_profit = go.Scatter(x=self.realized_pnl_df.index,
                                     y=self.realized_pnl_df[i],
                                     xaxis='x4', yaxis='y4',
                                     name=i)

            self.data.append(p_re_profit)

        for i in self.holding_pnl_df:
            self.holding_pnl_df.sort_index(inplace=True)

            p_unre_profit = go.Scatter(x=self.holding_pnl_df.index,
                                       y=self.holding_pnl_df[i],
                                       xaxis='x4', yaxis='y4',
                                       name=i)

            self.data.append(p_unre_profit)

        for i in self.commission_df:
            self.commission_df.sort_index(inplace=True)
            p_commission = go.Scatter(x=self.commission_df.index,
                                      y=self.commission_df[i],
                                      xaxis='x4', yaxis='y4',
                                      name=i, visible='legendonly')

            self.data.append(p_commission)
        p_total = go.Scatter(x=self.balance_df.index,
                             y=self.balance_df.balance,
                             xaxis='x6', yaxis='y6', name='balance')

        p_cash = go.Scatter(x=self.cash_df.index,
                            y=self.cash_df.cash,
                            xaxis='x6', yaxis='y6', name='cash')

        self.data.append(p_total)
        self.data.append(p_cash)

        layout = go.Layout(
            xaxis2=dict(
                domain=[0, 1],
                anchor='y2',
                scaleanchor='x2'
            ),
            xaxis3=dict(
                domain=[0, 1],
                anchor='y3',
                scaleanchor='x2'
            ),
            xaxis4=dict(
                domain=[0, 1],
                anchor='y4',
                scaleanchor='x2'
            ),
            xaxis6=dict(
                domain=[0, 1],
                anchor='y6',
                scaleanchor='x2'
            ),
            yaxis2=dict(
                domain=[0, 0.15],
                scaleanchor='x2'
            ),
            yaxis3=dict(
                domain=[0.15, 0.65],
                scaleanchor='x2'
            ),
            yaxis4=dict(
                domain=[0.65, 0.85],
                scaleanchor='x2'
            ),
            yaxis5=dict(
                domain=[0.15, 0.65],
                side='right',
                range=[0, 10000000],
                overlaying='y3',
                tickvals=[0, 1000000, 2000000, 2500000],
                showgrid=False,
                scaleanchor='x2'
            ),
            yaxis6=dict(
                domain=[0.85, 1],
                scaleanchor='x2'
            )
        )
        fig = go.Figure(data=self.data, layout=layout)

        if notebook:
            import plotly
            plotly.offline.init_notebook_mode()
            py.iplot(fig, filename='OnePy_plot.html', validate=False)
        else:
            py.plot(fig, filename='OnePy_plot.html', validate=False)
