import plotly.offline as py
import plotly.tools as tls
import pandas as pd
import plotly.figure_factory as FF

import plotly.graph_objs as go

class plotter_Meta(object):
    def __init__(self):
        pass


class plotter(plotter_Meta):
    def __init__(self,latest_bar_dict,enquity_curve,tlog,positions,holdings):
        self.latest_bar_dict = latest_bar_dict
        self.enquity_curve = enquity_curve
        self.tlog = tlog
        self.positions = positions
        self.holdings = holdings
        self.data = []
        self.updatemenus = []
        pass

    def plot(self,symbol=None,engine='plotly',notebook=False):
        if engine == 'plotly':
            if type(symbol) == str:
                df = pd.DataFrame(self.latest_bar_dict[symbol])
                df.set_index('date',inplace=True)
                df.index = pd.DatetimeIndex(df.index)
                p_symbol = go.Scatter(x=df.index,y=df.close,
                                         xaxis='x3',yaxis='y3',name=symbol)
                p_volume = go.Bar(x=df.index,y=df['volume'],
                                  xaxis='x3',yaxis='y5',opacity=0.5,name='volume')
                self.data.append(p_symbol)
                self.data.append(p_volume)

            if type(symbol) == list:
                for i in symbol:
                    df = pd.DataFrame(self.latest_bar_dict[i])
                    df.set_index('date',inplace=True)
                    df.index = pd.DatetimeIndex(df.index)
                    p_symbol = go.Scatter(x=df.index,y=df.close,
                                             xaxis='x3',yaxis='y3',name=i)
                    p_volume = go.Bar(x=df.index,y=df['volume'],
                                      xaxis='x3',yaxis='y5',opacity=0.5,name=i+'volume')
                    self.data.append(p_symbol)
                    self.data.append(p_volume)

            for i in self.holdings:
                p_holdings = go.Scatter(x=self.holdings.index,
                                     y=self.holdings[i],
                                     xaxis='x2',yaxis='y2',name=i)
                self.data.append(p_holdings)

            p_returns = go.Scatter(x=self.enquity_curve.index,
                                   y=self.enquity_curve.returns,
                                   xaxis='x4',yaxis='y4',name='returns')
            self.data.append(p_returns)

            layout = go.Layout(
                xaxis2=dict(
                    domain=[0, 1],
                    anchor='y2',
                ),
                xaxis3=dict(
                    domain=[0, 1],
                    anchor='y3'
                ),
                xaxis4=dict(
                    domain=[0, 1],
                    anchor='y4'
                ),
                yaxis2=dict(
                    domain=[0, 0.2],
                ),
                yaxis3=dict(
                    domain=[0.2, 0.8]
                ),
                yaxis4=dict(
                    domain=[0.8, 1],
                ),
                yaxis5=dict(
                    domain=[0.2, 0.8],
                    side='right',
                    range=[0,10000000],
                    overlaying='y3',
                    tickvals=[0,1000000,2000000,2500000],
                    showgrid=False
                )
            )
            fig = go.Figure(data=self.data, layout=layout)
            if notebook:
                import plotly
                plotly.offline.init_notebook_mode()
                py.iplot(fig, filename='testplot', validate=False)
            else:
                py.plot(fig, filename='testplot', validate=False)

    def plot_log(self,symbol,engine='plotly',notebook=False):
        if engine == 'plotly':
            def draw(i):
                tlog = self.tlog[self.tlog['symbol'] == i]
                ltlog = tlog[tlog['s_type'] == 'LONG']
                stlog = tlog[tlog['s_type'] == 'SHORT']
                price = go.Scatter(x=tlog.index,
                                   y=tlog['price'],
                                   name=i+'_price',
                                   xaxis='x3',yaxis='y3')
                qty = go.Scatter(x=tlog.index,
                                 y=tlog['qty'],
                                 name=i+'_qty',
                                 xaxis='x4',yaxis='y4')
                LONG_cur_positions = go.Scatter(x=ltlog.index,
                                 y=ltlog['cur_positions'],
                                 name=i+'LONG_cur_positions',
                                 xaxis='x4',yaxis='y4')
                SHORT_cur_positions = go.Scatter(x=stlog.index,
                                 y=stlog['cur_positions'],
                                 name=i+'SHORT_cur_positions',
                                 xaxis='x4',yaxis='y4')
                LONG_period = go.Scatter(x=ltlog.index,
                                 y=ltlog['period'].astype(int)/(60*60*24*10**9),
                                 name=i+'LONG_period',
                                 xaxis='x2',yaxis='y2')
                SHORT_period = go.Scatter(x=stlog.index,
                                 y=stlog['period'].astype(int)/(60*60*24*10**9),
                                 name=i+'SHORT_period',
                                 xaxis='x2',yaxis='y2')
                LONG_PnL = go.Scatter(x=ltlog.index,
                                 y=ltlog['PnL'],
                                 name=i+'LONG_PnL',
                                 xaxis='x2',yaxis='y2')
                SHORT_PnL = go.Scatter(x=stlog.index,
                                 y=stlog['PnL'],
                                 name=i+'SHORT_PnL',
                                 xaxis='x2',yaxis='y2')
                self.data.append(price)
                self.data.append(qty)
                self.data.append(LONG_cur_positions)
                self.data.append(SHORT_cur_positions)
                self.data.append(LONG_period)
                self.data.append(SHORT_period)
                self.data.append(LONG_PnL)
                self.data.append(SHORT_PnL)

            if type(symbol) == list:
                for i in symbol:
                    draw(i)
            if type(symbol) == str:
                    draw(symbol)

            layout = go.Layout(updatemenus=self.updatemenus,
                xaxis2=dict(
                    domain=[0, 1],
                    anchor='y2',
                ),
                xaxis3=dict(
                    domain=[0, 1],
                    anchor='y3'
                ),
                xaxis4=dict(
                    domain=[0, 1],
                    anchor='y4'
                ),
                yaxis2=dict(
                    domain=[0, 0.3],
                ),
                yaxis3=dict(
                    domain=[0.3, 0.6]
                ),
                yaxis4=dict(
                    domain=[0.6, 1],
                )
            )
            fig = go.Figure(data=self.data, layout=layout)
            if notebook:
                import plotly
                plotly.offline.init_notebook_mode()
                py.iplot(fig, filename='testplot', validate=False)
            else:
                py.plot(fig, filename='testplot', validate=False)



#
# p = pd.read_pickle('/Users/chandler/Desktop/test.pkl')
# df = pd.read_csv('/Users/chandler/Desktop/stock/data_csv/000006.csv',parse_dates=True,index_col=0)
# equity = p['equity']
# log = p['log']
# positions = p['positions']
# holdings = p['holdings']
#
# # d1 = go.Ohlc(open=df.open, high=df.high, low=df.low, close=df.close,x=df.index,
# #                     increasing=dict(name='sss'),xaxis='x3',yaxis='y3'
# #                     )
# d1 = go.Scatter(x=df.index,y=df.close,xaxis='x3',yaxis='y3'
#                     )
# d2 = go.Scatter(x=positions.index,y=positions,xaxis='x2',yaxis='y2',name='asdfasdf')
# # d3 = go.Scatter(x=equity.index,y=equity.total,xaxis='x2',yaxis='y2')
# d4 = go.Scatter(x=equity.index,y=equity.returns,xaxis='x4',yaxis='y4')
# d5 = go.Bar(x=df.index,y=df['volume'],xaxis='x3',yaxis='y5',opacity=0.5)
#
# data=[d4,d1,d2,d3,d5]
#
#
# layout = go.Layout(
#     xaxis2=dict(
#         domain=[0, 1],
#         anchor='y2',
#     ),
#     xaxis3=dict(
#         domain=[0, 1],
#         anchor='y3'
#     ),
#     xaxis4=dict(
#         domain=[0, 1],
#         anchor='y4'
#     ),
#     yaxis2=dict(
#         domain=[0, 0.2],
#     ),
#     yaxis3=dict(
#         domain=[0.2, 0.8]
#     ),
#     yaxis4=dict(
#         domain=[0.8, 1],
#     ),
#     yaxis5=dict(
#         domain=[0.2, 0.8],
#         side='right',
#         range=[0,10000000],
#         overlaying='y3',
#         tickvals=[0,1000000,2000000],
#         showgrid=False
#
#     )
# )
# fig = go.Figure(data=data, layout=layout)
#
#
# # fig['layout'].update(height=900, width=1900, title='OnePy')
#
# py.plot(fig, filename='testplot', validate=False,)
