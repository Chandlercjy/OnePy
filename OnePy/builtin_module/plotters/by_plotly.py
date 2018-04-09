
import pandas as pd
from plotly import graph_objs as go
from plotly import offline as py

from OnePy.environment import Environment


class PlotBase(object):
    env = Environment


class Plotly(PlotBase):

    def __init__(self):
        super().__init__()
        # TODO:index需要转成datetime，不然会画错
        self.ohlc = self.env.recorder.ohlc.dataframe
        self.balance_df = self.env.recorder.balance.dataframe()
        self.cash_df = self.env.recorder.cash.dataframe()
        self.positions_df = self.env.recorder.position.dataframe()
        self.realized_pnl_df = self.env.recorder.realized_pnl.dataframe()
        self.holding_pnl_df = self.env.recorder.holding_pnl.dataframe()
        self.commission_df = self.env.recorder.commission.dataframe()
        self.data = []
        self.updatemenus = []

    def plot(self, instrument=None, engine='plotly', notebook=False):
        if engine == 'plotly':
            if isinstance(instrument, str):
                df = self.ohlc(instrument)
                df.index = pd.DatetimeIndex(df.index)
                p_symbol = go.Scatter(x=df.index, y=df.close,
                                      xaxis='x3', yaxis='y3', name=instrument)
                p_volume = go.Bar(x=df.index, y=df['volume'],
                                  xaxis='x3', yaxis='y5', opacity=0.5, name='volume')
                self.data.append(p_symbol)
                self.data.append(p_volume)

            if isinstance(instrument, list):
                for i in instrument:
                    df = self.ohlc(instrument)
                    df.index = pd.DatetimeIndex(df.index)
                    p_symbol = go.Scatter(x=df.index, y=df.close,
                                          xaxis='x3', yaxis='y3', name=i)
                    p_volume = go.Bar(x=df.index, y=df['volume'],
                                      xaxis='x3', yaxis='y5',
                                      opacity=0.5, name=i + 'volume')
                    self.data.append(p_symbol)
                    self.data.append(p_volume)

            for i in self.positions_df:
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
                p_unre_profit = go.Scatter(x=self.holding_pnl_df.index,
                                           y=self.holding_pnl_df[i],
                                           xaxis='x4', yaxis='y4',
                                           name=i)

                self.data.append(p_unre_profit)

            for i in self.commission_df:
                p_commission = go.Scatter(x=self.commission_df.index,
                                          y=self.commission_df[i],
                                          xaxis='x4', yaxis='y4',
                                          name=i)

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

                # def plot_log(self,symbol,engine='plotly',notebook=False):
                #     if engine == 'plotly':
                #         def draw(i):
                #             tlog = self.tlog[self.tlog['symbol'] == i]
                #             ltlog = tlog[tlog['s_type'] == 'LONG']
                #             stlog = tlog[tlog['s_type'] == 'SHORT']
                #             price = go.Scatter(x=tlog.index,
                #                                y=tlog['price'],
                #                                name=i+'_price',
                #                                xaxis='x3',yaxis='y3')
                #             qty = go.Scatter(x=tlog.index,
                #                              y=tlog['qty'],
                #                              name=i+'_qty',
                #                              xaxis='x4',yaxis='y4')
                #             LONG_cur_positions = go.Scatter(x=ltlog.index,
                #                              y=ltlog['cur_positions'],
                #                              name=i+'LONG_cur_positions',
                #                              xaxis='x4',yaxis='y4')
                #             SHORT_cur_positions = go.Scatter(x=stlog.index,
                #                              y=stlog['cur_positions'],
                #                              name=i+'SHORT_cur_positions',
                #                              xaxis='x4',yaxis='y4')
                #             LONG_period = go.Scatter(x=ltlog.index,
                #                              y=ltlog['period'].astype(int)/(60*60*24*10**9),
                #                              name=i+'LONG_period',
                #                              xaxis='x2',yaxis='y2')
                #             SHORT_period = go.Scatter(x=stlog.index,
                #                              y=stlog['period'].astype(int)/(60*60*24*10**9),
                #                              name=i+'SHORT_period',
                #                              xaxis='x2',yaxis='y2')
                #             LONG_PnL = go.Scatter(x=ltlog.index,
                #                              y=ltlog['PnL'],
                #                              name=i+'LONG_PnL',
                #                              xaxis='x2',yaxis='y2')
                #             SHORT_PnL = go.Scatter(x=stlog.index,
                #                              y=stlog['PnL'],
                #                              name=i+'SHORT_PnL',
                #                              xaxis='x2',yaxis='y2')
                #             self.data.append(price)
                #             self.data.append(qty)
                #             self.data.append(LONG_cur_positions)
                #             self.data.append(SHORT_cur_positions)
                #             self.data.append(LONG_period)
                #             self.data.append(SHORT_period)
                #             self.data.append(LONG_PnL)
                #             self.data.append(SHORT_PnL)
                #
                #         if type(symbol) == list:
                #             for i in symbol:
                #                 draw(i)
                #         if type(symbol) == str:
                #                 draw(symbol)
                #
                #         layout = go.Layout(updatemenus=self.updatemenus,
                #             xaxis2=dict(
                #                 domain=[0, 1],
                #                 anchor='y2',
                #             ),
                #             xaxis3=dict(
                #                 domain=[0, 1],
                #                 anchor='y3'
                #             ),
                #             xaxis4=dict(
                #                 domain=[0, 1],
                #                 anchor='y4'
                #             ),
                #             yaxis2=dict(
                #                 domain=[0, 0.3],
                #             ),
                #             yaxis3=dict(
                #                 domain=[0.3, 0.6]
                #             ),
                #             yaxis4=dict(
                #                 domain=[0.6, 1],
                #             )
                #         )
                #         fig = go.Figure(data=self.data, layout=layout)
                #         if notebook:
                #             import plotly
                #             plotly.offline.init_notebook_mode()
                #             py.iplot(fig, filename='testplot.html', validate=False)
                #         else:
                #             py.plot(fig, filename='testplot.html', validate=False)
