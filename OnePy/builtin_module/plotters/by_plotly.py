
import pandas as pd
import plotly
from plotly import offline as py

from OnePy.sys_module.metabase_env import OnePyEnvBase


class PlotBase(OnePyEnvBase):

    def __init__(self):
        super().__init__()
        self.positions_df = self.env.recorder.position.dataframe()
        self.holding_pnl_df = self.env.recorder.holding_pnl.dataframe()
        self.commission_df = self.env.recorder.commission.dataframe()
        self.margin_df = self.env.recorder.margin.dataframe()
        self.data = []
        self.updatemenus = []
        self.balance_df = self.env.recorder.balance.dataframe()
        self.cash_df = self.env.recorder.cash.dataframe()
        self.balance_df.columns = ['balance']
        self.cash_df.columns = ['cash']

    @property
    def realized_pnl_df(self):
        trade_log = self.env.recorder.match_engine.generate_trade_log()
        trade_log.dropna(inplace=True)
        df = trade_log[['exit_date', 're_pnl']].copy()
        df.rename(columns=dict(exit_date='date'), inplace=True)
        df.set_index('date', drop=True, inplace=True)
        df.index = pd.to_datetime(df.index)

        return df

    @property
    def returns_df(self):
        returns_df = self.balance_df.pct_change(
        ).dropna()

        returns_df.columns = ['returns']

        return returns_df

    def ohlc_df(self, ticker):
        ohlc = self.env.readers[ticker].load(
            self.env.fromdate, self.env.todate, self.env.sys_frequency)
        dataframe = pd.DataFrame((i for i in ohlc))
        dataframe.set_index('date', inplace=True)
        dataframe.index = pd.to_datetime(dataframe.index)

        return dataframe


class Plotly(PlotBase):
    """
    Depreciated
    """

    def plot2(self, ticker=None, notebook=False):

        returns_df = self.balance_df.pct_change(
        ).dropna()

        returns_df.columns = ['returns']
        fig = plotly.tools.make_subplots(
            rows=5, cols=2,
            shared_xaxes=True,
            vertical_spacing=0.001)

        fig['layout'].update(height=1500)

        self.append_trace(fig, self.positions_df, 2, 1)
        self.append_trace(fig, self.balance_df, 3, 1)
        self.append_trace(fig, self.holding_pnl_df, 4, 1)
        self.append_trace(fig, self.commission_df, 5, 1)
        self.append_trace(fig, self.margin_df, 1, 1)
        self.append_trace(fig, returns_df, 2, 2, 'bar')
        # fig['layout']['showlegend'] = True

        if notebook:
            plotly.offline.init_notebook_mode()
            py.iplot(fig, filename='OnePy_plot.html', validate=False)
        else:
            py.plot(fig, filename='OnePy_plot.html', validate=False)

    def append_trace(self, figure, df_list, row, col, plot_type='scatter', legendly_visible: bool=False):

        visible = True if legendly_visible is False else 'legendonly'

        if not isinstance(df_list, list):
            df_list = [df_list]

        for dataframe in df_list:
            dataframe.sort_index(inplace=True)
            name = dataframe.columns[0]
            series = dataframe[name]
            result = dict(
                x=series.index,
                y=series.values,
                name=name,
                type=plot_type,
                visible=visible,
                legendgroup=f'{name[:4]}')

            figure.append_trace(result, row, col)

    def append_candlestick_trace(self, figure, dataframe, row, col, ticker):

        dataframe.sort_index(inplace=True)
        result = dict(
            x=dataframe.index,
            open=dataframe.open,
            high=dataframe.high,
            low=dataframe.low,
            close=dataframe.close,
            type='candlestick'
        )

        figure.append_trace(result, row, col)

    def plot(self, ticker=None, notebook=False):

        fig = plotly.tools.make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.001,
            specs=[[{}],
                   [{}],
                   [{'rowspan': 2}],
                   [None],
                   [{}]],)

        # fig['layout'].update(height=1500)

        if isinstance(ticker, str):
            ticker = [ticker]

        for i in ticker:
            close_df = self.ohlc_df(i)[['close']]
            close_df.columns = [i]
            #  volume_df = self.ohlc_df(i)[['volume']]
            #  volume_df.columns = [i+' volume']
            self.append_trace(fig, close_df, 3, 1)
            #  self.append_trace(fig, volume_df, 3, 1,
            #  plot_type='bar', legendly_visible=True)
            #  fig['data'][-1].update(dict(yaxis='y6', opacity=0.5))

        #  for i in ticker:
            #  self.append_candlestick_trace(fig, self.ohlc_df(i), 3, 1, i)

        self.append_trace(fig, self.balance_df, 1, 1)
        self.append_trace(fig, self.cash_df, 1, 1)
        self.append_trace(fig, self.holding_pnl_df, 2, 1)
        self.append_trace(fig, self.commission_df, 2,
                          1, legendly_visible=True)
        self.append_trace(fig, self.positions_df, 5, 1)

        total_holding_pnl = sum((i[i.columns[0]] for i in self.holding_pnl_df))
        total_holding_pnl = pd.DataFrame(total_holding_pnl)
        total_holding_pnl.columns = ['total_holding_pnl']
        self.append_trace(fig, total_holding_pnl, 2, 1)

        fig['layout']['yaxis'].update(
            dict(overlaying='y3', side='right', showgrid=False))
        # fig['layout']['xaxis']['type'] = 'category'
        # fig['layout']['xaxis']['rangeslider']['visible'] = False
        # fig['layout']['xaxis']['tickangle'] = 45
        fig['layout']['xaxis']['visible'] = False
        fig['layout']['hovermode'] = 'closest'
        fig['layout']['xaxis']['rangeslider']['visible'] = False

        if notebook:
            plotly.offline.init_notebook_mode()
            py.iplot(fig, filename='OnePy_plot.html', validate=False)
        else:
            py.plot(fig, filename='OnePy_plot.html', validate=False)
