from matplotlib import pyplot as plt

from OnePy.plotter.plotbase import plotBase

#
# class matplotlib(plotBase):
#     def __init__(self, fill):
#         super(matplotlib, self).__init__()
#         self.margin_dict = fill.margin_dict
#         self.position_dict = fill.position_dict
#         self.avg_price_dict = fill.avg_price_dict
#         self.unre_profit_dict = fill.unre_profit_dict
#         self.re_profit_dict = fill.re_profit_dict
#         self.cash_list = fill.cash_list
#         self.total_list = fill.total_list
#
#     def plot(self, name, instrument):
#         if 'margin' in name:
#             df1 = self.__to_df(self.margin_dict, instrument)
#             df1.plot(figsize=(15, 3))
#         if 'position' in name:
#             df2 = self.__to_df(self.position_dict, instrument)
#             df2.plot(figsize=(15, 3))
#         if 'un_profit' in name:
#             df3 = self.__to_df(self.unre_profit_dict, instrument)
#             df3.plot(figsize=(15, 3))
#         if 're_profit' in name:
#             df4 = self.__to_df(self.re_profit_dict, instrument)
#             df4.plot(figsize=(15, 3))
#         if 'cash' in name:
#             df5 = self.__to_df(self.cash_list, instrument)
#             df5.plot(figsize=(15, 3))
#         if 'total' in name:
#             df6 = self.__to_df(self.total_list, instrument)
#             df6.plot(figsize=(15, 3))
#         if 'avg_price' in name:
#             df66 = self.__to_df(self.avg_price_dict, instrument)
#             df66.plot(figsize=(15, 3))
#         if 'total_profit' in name:
#             df8 = self.deal_realizedPL(self.re_profit_dict, instrument)
#             df8.plot(figsize=(15, 3))
#         plt.show()