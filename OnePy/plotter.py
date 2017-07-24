#coding=utf8
import pandas as pd
import matplotlib.pyplot as plt

import plotly.offline as py
import plotly.tools as tls
import pandas as pd
import plotly.figure_factory as FF

import plotly.graph_objs as go


class plotBase(object):
    def __init__(self):
        pass

    def _to_df(self,data,instrument):
        try:
            data = data[instrument]
        except:
            pass

        df = pd.DataFrame(data)[1:]
        df.set_index('date',inplace=True)
        df.index = pd.DatetimeIndex(df.index)
        return df

    def deal_re_profit(self,d,instrument):
        df = pd.DataFrame(d[instrument])[1:]
        # df['re_profit'] = df[['re_profit']].cumsum()
        df = df.sort_index(ascending=False)
        df = df.drop_duplicates('date').sort_index()
        df.set_index('date',inplace=True)
        df.index = pd.DatetimeIndex(df.index)
        return df


class matplotlib(plotBase):
    def __init__(self, fill):
        super(matplotlib,self).__init__()
        self.margin_dict = fill.margin_dict
        self.position_dict = fill.position_dict
        self.avg_price_dict = fill.avg_price_dict
        self.unre_profit_dict = fill.unre_profit_dict
        self.re_profit_dict = fill.re_profit_dict
        self.cash_list = fill.cash_list
        self.total_list = fill.total_list



    def plot(self,name,instrument):
        if 'margin' in name:
            df1 = self._to_df(self.margin_dict,instrument)
            df1.plot(figsize=(15,3))
        if 'position' in name:
            df2 = self._to_df(self.position_dict,instrument)
            df2.plot(figsize=(15,3))
        if 'un_profit' in name:
            df3 = self._to_df(self.unre_profit_dict,instrument)
            df3.plot(figsize=(15,3))
        if 're_profit' in name:
            df4 = self._to_df(self.re_profit_dict,instrument)
            df4.plot(figsize=(15,3))
        if 'cash' in name:
            df5 = self._to_df(self.cash_list,instrument)
            df5.plot(figsize=(15,3))
        if 'total' in name:
            df6 = self._to_df(self.total_list,instrument)
            df6.plot(figsize=(15,3))
        if 'avg_price' in name:
            df66 = self._to_df(self.avg_price_dict,instrument)
            df66.plot(figsize=(15,3))
        if 'total_profit' in name:
            df8 = self.deal_re_profit(self.re_profit_dict,instrument)
            df8.plot(figsize=(15,3))
        plt.show()

class plotly(plotBase):
    def __init__(self,instrument,feed_list,fill):
        super(plotly,self).__init__()

        self.bar_dict = self._set_bar_dict(feed_list)

        self.total_df = self._to_df(fill.total_list,instrument)
        self.cash_df = self._to_df(fill.cash_list,instrument)
        self.positions_df = self._to_df(fill.position_dict,instrument)
        self.re_profit_df = self.deal_re_profit(fill.re_profit_dict,instrument)
        self.unre_profit_df = self._to_df(fill.unre_profit_dict,instrument)
        self.data = []
        self.updatemenus = []

    def _set_bar_dict(self,feed_list):
        d = {}
        for f in feed_list:
            d.update(f.bar_dict)
        return d


    def plot(self,instrument=None,engine='plotly',notebook=False):
        if engine == 'plotly':
            if type(instrument) == str:
                df = pd.DataFrame(self.bar_dict[instrument])
                df.set_index('date',inplace=True)
                df.index = pd.DatetimeIndex(df.index)
                p_symbol = go.Scatter(x=df.index,y=df.close,
                                         xaxis='x3',yaxis='y3',name=instrument)
                # p_volume = go.Bar(x=df.index,y=df['volume'],
                #                   xaxis='x3',yaxis='y5',opacity=0.5,name='volume')
                self.data.append(p_symbol)
                # self.data.append(p_volume)


            if type(instrument) == list:
                for i in instrument:
                    df = pd.DataFrame(self.bar_dict[i])
                    df.set_index('date',inplace=True)
                    df.index = pd.DatetimeIndex(df.index)
                    p_symbol = go.Scatter(x=df.index,y=df.close,
                                             xaxis='x3',yaxis='y3',name=i)
                    p_volume = go.Bar(x=df.index,y=df['volume'],
                                      xaxis='x3',yaxis='y5',
                                      opacity=0.5,name=i+'volume')
                    self.data.append(p_symbol)
                    self.data.append(p_volume)

            for i in self.positions_df:
                p_position = go.Scatter(x=self.positions_df.index,
                                     y=self.positions_df[i],
                                     xaxis='x2',yaxis='y2',name=i)

            p_total = go.Scatter(x=self.total_df.index,
                                   y=self.total_df.total,
                                   xaxis='x6',yaxis='y6',name='total')

            p_cash = go.Scatter(x=self.cash_df.index,
                                   y=self.cash_df.cash,
                                   xaxis='x6',yaxis='y6',name='cash')

            p_re_profit = go.Scatter(x=self.re_profit_df.index,
                                   y=self.re_profit_df.re_profit,
                                   xaxis='x4',yaxis='y4',
                                   name='realized_profit')

            p_unre_profit = go.Scatter(x=self.unre_profit_df.index,
                                   y=self.unre_profit_df.unre_profit,
                                   xaxis='x4',yaxis='y4',
                                   name='unrealized_profit')

            self.data.append(p_position)
            self.data.append(p_total)
            self.data.append(p_cash)
            self.data.append(p_unre_profit)
            self.data.append(p_re_profit)

            layout = go.Layout(
                xaxis2=dict(
                    domain=[0, 1],
                    anchor='y2',
                    scaleanchor = 'x2'
                ),
                xaxis3=dict(
                    domain=[0, 1],
                    anchor='y3',
                    scaleanchor = 'x2'
                ),
                xaxis4=dict(
                    domain=[0, 1],
                    anchor='y4',
                    scaleanchor = 'x2'
                ),
                xaxis6=dict(
                    domain=[0, 1],
                    anchor='y6',
                    scaleanchor = 'x2'
                ),
                yaxis2=dict(
                    domain=[0, 0.15],
                    scaleanchor = 'x2'
                ),
                yaxis3=dict(
                    domain=[0.15, 0.65],
                    scaleanchor = 'x2'
                ),
                yaxis4=dict(
                    domain=[0.65, 0.85],
                    scaleanchor = 'x2'
                ),
                yaxis5=dict(
                    domain=[0.15, 0.65],
                    side='right',
                    range=[0,10000000],
                    overlaying='y3',
                    tickvals=[0,1000000,2000000,2500000],
                    showgrid=False,
                    scaleanchor = 'x2'
                ),
                yaxis6=dict(
                    domain=[0.85, 1],
                    scaleanchor = 'x2'
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
