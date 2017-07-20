import pandas as pd
import matplotlib.pyplot as plt

class matplotlib(object):
    def __init__(self, fill):
        self.margin_dict = fill.margin_dict
        self.position_dict = fill.position_dict
        self.avg_price_dict = fill.avg_price_dict
        self.unre_profit_dict = fill.unre_profit_dict
        self.re_profit_dict = fill.re_profit_dict
        self.cash_list = fill.cash_list
        self.total_list = fill.total_list
        self.return_list = fill.return_list

    def _to_df(self,data,instrument):
        try:
            data = data[instrument]
        except:
            pass

        df = pd.DataFrame(data)
        df.set_index('date',inplace=True)
        return df

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
        if 'return' in name:
            df7 = self._to_df(self.return_list,instrument)
            df7.plot(figsize=(15,3))
        plt.show()
