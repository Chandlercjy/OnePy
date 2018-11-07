
from collections import defaultdict

import OnePy as op
from OnePy.custom_module.cleaner_talib import Talib


class DemoTestStrategy(op.StrategyBase):

    def __init__(self):
        super().__init__()

        self.params = dict(sma1=25,
                           sma2=9)

        self.set_params(self.params)

    def set_params(self, params: dict):
        self.params = params
        self.sma1 = Talib(ind='SMA', frequency='H1',
                          params=dict(timeperiod=params['sma1']),
                          buffer_day=20).calculate

        self.sma2 = Talib(ind='SMA', frequency='D',
                          params=dict(timeperiod=params['sma2']),
                          buffer_day=20).calculate

    def handle_bar(self):
        for ticker in self.env.tickers:
            sma1 = self.sma1(ticker)
            sma2 = self.sma2(ticker)

            if sma1 > sma2:
                self.buy(1, ticker, takeprofit=10, stoploss=10)
                self.buy(1, ticker, takeprofit_pct=0.01, trailingstop=10)
                self.buy(1, ticker, price_pct=0.1, takeprofit_pct=0.01)
                self.short(1, ticker, takeprofit=10, trailingstop_pct=0.03)
                self.short(1, ticker, stoploss_pct=0.02)
            else:
                self.sell(1, ticker, price_pct=0.1)
                self.sell(99, ticker)
                self.cover(3, ticker, price_pct=0.02)

                self.cancel_tst(ticker, 'long', takeprofit=True)
                self.cancel_pending(ticker, 'long', above_price=0)


START, END = '2016-01-05', '2016-01-21'

FREQUENCY = 'M30'
TICKER_LIST = ['EUR_USD']
INITIAL_CASH = 2000


go = op.backtest.forex(TICKER_LIST, FREQUENCY,
                       INITIAL_CASH, START, END, 'oanda')
DemoTestStrategy()


# forward_analysis(go, START, END, 2, 3)
# go.forward_analysis.run(START, 3, 2, 5)
# go.show_today_signals()
# go.sunny()
# go.output.save_result('backtest_forex.pkl')


# go.output.summary2()
# go.output.analysis.trade_analysis()

# go.output.plot('EUR_USD')
# go.output.plot(TICKER_LIST, 'plotly')


# || 正在初始化OnePy
# || =============== OnePy初始化成功！ ===============
# || 开始寻找OnePiece之旅~~~
# || cleaners警告，可能遇到周末导致无法next
# || cleaners警告，可能遇到周末导致无法next
# || cleaners警告，可能遇到周末导致无法next
# || cleaners警告，可能遇到周末导致无法next
# ||
# ||
# || +--------------------------------+
# || |Fromdate           |  2016-01-05|
# || |Todate             |  2016-01-21|
# || |Initial_Value      |    $2000.00|
# || |Final_Value        |    $1991.33|
# || |Total_Return       |     -0.433%|
# || |Max_Drawdown       |      2.725%|
# || |Max_Duration       |     14 days|
# || |Max_Drawdown_Date  |  2016-01-20|
# || |Sharpe_Ratio       |       -1.37|
# || +--------------------------------+
# || +---------------------------------------+
# || |Start_date                |  2016-01-05|
# || |End_date                  |  2016-01-21|
# || |Initial_balance           |    $2000.00|
# || |End_balance               |    $1991.33|
# || |Total_return              |      -0.43%|
# || |Total_net_pnl             |      -$8.67|
# || |Total_commission          |       $0.19|
# || |Total_trading_days        |     15 days|
# || |Max_drawdown              |       2.73%|
# || |Max_drawdown_date         |  2016-01-20|
# || |Max_duration_in_drawdown  |     14 days|
# || |Max_margin                |      $14.76|
# || |Max_win_holding_pnl       |      $13.26|
# || |Max_loss_holding_pnl      |     -$37.73|
# || |Sharpe_ratio              |       -1.37|
# || |Sortino_ratio             |       -1.96|
# || |Number_of_trades          |        1264|
# || |Number_of_daily_trades    |       84.27|
# || |Number_of_profit_days     |     15 days|
# || |Number_of_loss_days       |      0 days|
# || |Avg_daily_pnl             |      -$0.58|
# || |Avg_daily_commission      |       $0.01|
# || |Avg_daily_return          |      -0.03%|
# || |Avg_daily_std             |      -0.03%|
# || |Annual_compound_return    |      -7.52%|
# || |Annual_average_return     |      -7.82%|
# || |Annual_std                |      -0.48%|
# || |Annual_pnl                |    -$145.61|
# || +---------------------------------------+
# ||                               All Trades Long Trades Short Trades
# || Total_number_of_trades              1264         632          632
# || Total_net_pnl                     -$7.84     -$11.54        $3.69
# || Ratio_avg_win_avg_loss              0.85        0.75         0.87
# || Profit_factor                       0.69        0.29         1.43
# || Percent_profitable                45.02%      28.16%       61.87%
# || Number_of_winning_trades             569         178          391
# || Number_of_losing_trades              693         454          239
# || Max_holding_period             4.85 days   4.85 days    4.62 days
# || Max_consecutive_winning_trade        126          47          126
# || Max_consecutive_losing_trade         104         102           95
# || Largest_winning_trade              $0.11       $0.11        $0.10
# || Largest_losing_trade              -$0.12      -$0.10       -$0.12
# || Gross_profit                      $17.39       $4.75       $12.64
# || Gross_loss                       -$25.04     -$16.19       -$8.85
# || Gross_commission                   $0.19       $0.09        $0.09
# || Expectancy_adjusted_ratio          -0.17       -0.51         0.16
# || Expectancy                        -$0.01      -$0.02        $0.01
# || Avg_winning_trade                  $0.03       $0.03        $0.03
# || Avg_net_pnl_per_trade             -$0.01      -$0.02        $0.01
# || Avg_losing_trade                  -$0.04      -$0.04       -$0.04
# || Avg_holding_period             2.14 days   1.96 days    3.10 days
# || python tests/test_forex_strategy.py  4.84s user 0.35s system 92% cpu 5.622 total
# || [Finished in 5 seconds]
