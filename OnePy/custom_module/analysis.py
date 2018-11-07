import json
from collections import defaultdict

import arrow
import numpy as np
import pandas as pd

from OnePy.constants import ActionType, OrderType
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.utils.memo_for_cache import memo

# mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
# mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


TRADING_DAYS_PER_YEAR = 252
RISK_FREE = 0


def get_sharpe_ratio(balance):
    data = balance.pct_change().dropna()
    ratio = (np.sqrt(TRADING_DAYS_PER_YEAR) *
             ((np.mean(data))-RISK_FREE) / np.std(data))

    return ratio[0]


def get_sortino_ratio(balance):
    data = balance.pct_change().dropna()
    negative = data[data < 0].dropna().values
    ratio = np.sqrt(TRADING_DAYS_PER_YEAR) * \
        (np.mean(data)-RISK_FREE) / np.std(negative)

    return ratio[0]


def get_drawdown_df(balance):
    drawdown_df = balance/balance.expanding().max()-1
    drawdown_df[np.isinf(drawdown_df)] = 0
    drawdown_df.rename(columns=dict(balance='drawdown'), inplace=True)

    return -drawdown_df


def get_max_drawdown(balance):
    return get_drawdown_df(balance).max().values[0]


def get_max_drawdown_date(balance):
    df = get_drawdown_df(balance)
    max_drawdown = get_max_drawdown(balance)
    date = df[df.drawdown == max_drawdown].index[0]

    return arrow.get(date).format('YYYY-MM-DD')


def get_max_duration_in_drawdown(balance):
    max_balance = balance.expanding().max()
    diff = max_balance.shift(-1) - max_balance
    diff.dropna(inplace=True)

    count = 0
    count_list = []

    for i in diff.values:
        if i <= 0:
            count += 1
        else:
            count_list.append(count)
            count = 0
    count_list.append(count)

    return max(count_list)


def add_dollar(value):
    if value < 0:
        return f'-${-value:.2f}'

    return f'${value:.2f}'


def add_percent(value):
    return f'{value*100:.2f}%'


def add_days(value):
    if isinstance(value, int):
        return f'{value} days'

    return f'{value:.2f} days'


def add_none(value):
    if isinstance(value, int):
        return str(value)

    return f'{value:.2f}'


def get_combine_total(series):
    dataframe_list = (i.values for i in series.dataframe())
    value = sum(dataframe_list)

    if isinstance(value, int):
        return np.array([0])
    else:
        return value


def consecutive_number(values: list, positive=True):
    direction = 1 if positive else -1

    count = 0
    count_list = []

    for i in values:
        if i*direction > 0:
            count += 1
        else:
            count_list.append(count)
            count = 0

    if not count_list:
        return 0

    return max(count_list)


def get_trade_period(tradelog):
    entry_date = arrow.get(tradelog.entry_date)
    exit_date = arrow.get(tradelog.exit_date)
    diff = exit_date - entry_date

    return diff


def process_log(trade_logs):

    log_dict = defaultdict(list)

    for log in trade_logs:
        log_dict['ticker'].append(log.ticker)
        log_dict['entry_date'].append(log.entry_date)
        log_dict['entry_price'].append(log.entry_price)
        log_dict['entry_type'].append(log.entry_type)
        log_dict['size'].append(log.size)
        log_dict['exit_date'].append(log.exit_date)
        log_dict['exit_price'].append(log.exit_price)
        log_dict['exit_type'].append(log.exit_type)
        log_dict['pl_points'].append(log.pl_points)
        log_dict['re_pnl'].append(log.re_pnl)
        log_dict['comm'].append(log.commission)

        period = get_trade_period(log)
        log_dict['holding_period'].append(period)

    total_series = pd.DataFrame(log_dict)  # type:pd.DataFrame
    profit_series = total_series[total_series.re_pnl > 0].re_pnl.values
    loss_series = total_series[total_series.re_pnl < 0].re_pnl.values

    if loss_series.size == 0:
        loss_series = np.array([0])

    if profit_series.size == 0:
        profit_series = np.array([0])

    total_net_pnl = (total_series.re_pnl - total_series.comm).values.sum()
    gross_profit = profit_series.sum()
    gross_loss = loss_series.sum()
    gross_commission = total_series.comm.values.sum()
    profit_factor = abs(gross_profit/gross_loss)
    total_number_of_trades = len(total_series)
    percent_profitable = len(profit_series)/len(total_series)
    number_of_winning_trades = len(profit_series)
    number_of_losing_trades = len(loss_series)
    avg_trade_net_pnl = total_net_pnl / total_number_of_trades
    avg_winning_trade = gross_profit/number_of_winning_trades
    avg_losing_trade = gross_loss/number_of_losing_trades
    ratio_avg_win_avg_loss = abs(avg_winning_trade / avg_losing_trade)
    largest_winning_trade = max(profit_series)
    largest_losing_trade = min(loss_series)
    max_consecutive_winning_trade = consecutive_number(
        total_series.re_pnl.values)
    max_consecutive_losing_trade = consecutive_number(
        total_series.re_pnl.values, False)
    avg_holding_period = total_series.dropna(
    ).holding_period.mean().total_seconds()/60/60/24
    max_holding_period_trade = total_series.dropna(
    ).holding_period.max().total_seconds()/60/60/24
    expectancy = avg_winning_trade*percent_profitable + \
        avg_losing_trade*(1-percent_profitable)
    expectancy_adjusted = expectancy/(-avg_losing_trade)

    result = dict(
        Total_net_pnl=add_dollar(total_net_pnl),
        Gross_profit=add_dollar(gross_profit),
        Gross_loss=add_dollar(gross_loss),
        Gross_commission=add_dollar(gross_commission),
        Profit_factor=add_none(profit_factor),
        Total_number_of_trades=add_none(total_number_of_trades),
        Percent_profitable=add_percent(percent_profitable),

        Number_of_winning_trades=add_none(number_of_winning_trades),
        Number_of_losing_trades=add_none(number_of_losing_trades),

        Avg_net_pnl_per_trade=add_dollar(avg_trade_net_pnl),
        Avg_winning_trade=add_dollar(avg_winning_trade),
        Avg_losing_trade=add_dollar(avg_losing_trade),
        Avg_holding_period=add_days(avg_holding_period),
        Ratio_avg_win_avg_loss=add_none(ratio_avg_win_avg_loss),
        Largest_winning_trade=add_dollar(largest_winning_trade),
        Largest_losing_trade=add_dollar(largest_losing_trade),
        Max_consecutive_winning_trade=add_none(max_consecutive_winning_trade),
        Max_consecutive_losing_trade=add_none(max_consecutive_losing_trade),
        Max_holding_period=add_days(max_holding_period_trade),
        Expectancy=add_dollar(expectancy),
        Expectancy_adjusted_ratio=add_none(expectancy_adjusted)
    )

    return {key: [value] for key, value in result.items()}


class AmazingAnalysis(OnePyEnvBase):

    def __init__(self):
        self.env.recorder.match_engine.generate_trade_log()
        self.balance = self.env.recorder.balance.dataframe()
        self.trade_log = self.env.recorder.match_engine.finished_log

    @memo('general_summary')
    def general_summary(self) -> dict:
        daily_basis_balance = self.balance.resample('D').last().dropna()

        start_date = arrow.get(self.balance.index[0]).format('YYYY-MM-DD')
        end_date = arrow.get(self.balance.index[-1]).format('YYYY-MM-DD')
        initial_balance = self.balance.values[0][0]
        end_balance = self.balance.values[-1][0]
        total_return = end_balance / initial_balance - 1
        total_net_pnl = end_balance-initial_balance
        total_commission = self.env.recorder.commission.total_value()
        total_trading_days = len(daily_basis_balance)

        sharpe_ratio = get_sharpe_ratio(daily_basis_balance)
        sortino_ratio = get_sortino_ratio(daily_basis_balance)

        max_drawdown = get_max_drawdown(self.balance)
        max_drawdown_date = get_max_drawdown_date(self.balance)
        max_duration_in_drawdown = get_max_duration_in_drawdown(
            daily_basis_balance)
        max_margin = get_combine_total(self.env.recorder.margin).max()
        max_win_holding_pnl = get_combine_total(
            self.env.recorder.holding_pnl).max()
        max_loss_holding_pnl = get_combine_total(
            self.env.recorder.holding_pnl).min()

        number_of_trades = len(self.trade_log)
        number_of_profit_days = len(
            daily_basis_balance[daily_basis_balance.pct_change() > 0])
        number_of_loss_days = total_trading_days-number_of_profit_days
        number_of_daily_trades = number_of_trades/total_trading_days
        avg_daily_pnl = total_net_pnl/total_trading_days
        avg_daily_commission = total_commission / total_trading_days

        avg_daily_log_return = np.log(
            daily_basis_balance.shift(-1) / daily_basis_balance).dropna().mean()[0]
        avg_daily_return = np.exp(avg_daily_log_return)-1

        avg_daily_std = daily_basis_balance.pct_change().mean()[0]

        annual_coumpond_return = np.exp(
            avg_daily_log_return*TRADING_DAYS_PER_YEAR)-1
        annual_average_return = avg_daily_return*TRADING_DAYS_PER_YEAR
        annual_std = avg_daily_std*np.sqrt(TRADING_DAYS_PER_YEAR)
        annual_pnl = avg_daily_pnl*TRADING_DAYS_PER_YEAR

        general_result = dict(
            Start_date=start_date,
            End_date=end_date,

            Initial_balance=add_dollar(initial_balance),
            End_balance=add_dollar(end_balance),
            Total_return=add_percent(total_return),
            Total_net_pnl=add_dollar(total_net_pnl),
            Total_commission=add_dollar(total_commission),
            Total_trading_days=add_days(total_trading_days),

            Max_drawdown=add_percent(max_drawdown),
            Max_drawdown_date=max_drawdown_date,
            Max_duration_in_drawdown=add_days(max_duration_in_drawdown),
            Max_margin=add_dollar(max_margin),
            Max_win_holding_pnl=add_dollar(max_win_holding_pnl),
            Max_loss_holding_pnl=add_dollar(max_loss_holding_pnl),

            Sharpe_ratio=add_none(sharpe_ratio),
            Sortino_ratio=add_none(sortino_ratio),

            Number_of_trades=add_none(number_of_trades),
            Number_of_daily_trades=add_none(number_of_daily_trades),
            Number_of_profit_days=add_days(number_of_profit_days),
            Number_of_loss_days=add_days(number_of_loss_days),

            Avg_daily_pnl=add_dollar(avg_daily_pnl),
            Avg_daily_commission=add_dollar(avg_daily_commission),
            Avg_daily_return=add_percent(avg_daily_return),
            Avg_daily_std=add_percent(avg_daily_std),

            Annual_compound_return=add_percent(annual_coumpond_return),
            Annual_average_return=add_percent(annual_average_return),
            Annual_std=add_percent(annual_std),
            Annual_pnl=add_dollar(annual_pnl),
        )

        return general_result

    @memo('detail_summary')
    def detail_summary(self) -> pd.DataFrame:
        total_trade_log = self.trade_log
        long_trade_log = [
            i for i in total_trade_log if i.buy.action_type == ActionType.Buy]
        short_trade_log = [
            i for i in total_trade_log if i.buy.action_type == ActionType.Short]

        total = process_log(total_trade_log)
        short = process_log(
            short_trade_log) if short_trade_log else defaultdict(int)
        long = process_log(
            long_trade_log) if long_trade_log else defaultdict(int)

        for key in total:

            if isinstance(long[key], list):
                total[key] += long[key]
            else:
                total[key] += [None]

            if isinstance(short[key], list):
                total[key] += short[key]
            else:
                total[key] += [None]

        final = pd.DataFrame(total).T
        final.columns = ['All Trades', 'Long Trades', 'Short Trades']
        final.sort_index(ascending=False, inplace=True)

        return final

    @memo('full_trade_log')
    def get_full_trade_log(self) -> pd.DataFrame:

        log_dict = defaultdict(list)
        ohlc_dict = {}

        for log in self.trade_log:
            log_dict['ticker'].append(log.ticker)
            log_dict['entry_date'].append(log.entry_date)
            log_dict['entry_price'].append(log.entry_price)
            log_dict['entry_type'].append(log.entry_type)
            log_dict['size'].append(log.size)
            log_dict['exit_date'].append(log.exit_date)
            log_dict['exit_price'].append(log.exit_price)
            log_dict['exit_type'].append(log.exit_type)
            log_dict['pl_points'].append(log.pl_points)
            log_dict['re_pnl'].append(log.re_pnl)
            log_dict['comm'].append(log.commission)

            period = str(get_trade_period(log))
            log_dict['holding_period'].append(period)

            fromdate = log.entry_date
            todate = log.exit_date

            if log.ticker in ohlc_dict.keys():
                ohlc = ohlc_dict[log.ticker]
            else:
                ohlc = self.env.readers[log.ticker].load(
                    self.env.fromdate, self.env.todate, self.env.sys_frequency)
                ohlc = pd.DataFrame((i for i in ohlc))
                ohlc_dict[log.ticker] = ohlc

            data_high = ohlc.loc[ohlc.date >= fromdate].loc[ohlc.date <=
                                                            todate].high.values
            data_low = ohlc.loc[ohlc.date >= fromdate].loc[ohlc.date <=
                                                           todate].low.values

            if data_high.shape[0] != 0:
                if 'Short' in log.entry_type:

                    returns_diff = (-(log.exit_price -
                                      log.entry_price) / log.entry_price)
                    # diff of price
                    drawdown = (np.max(data_high) -
                                log.entry_price)/log.entry_price
                    run_up = -(np.min(data_low) - log.entry_price) / \
                        log.entry_price

                    if 'Trailing_stop' in log.exit_type:
                        price = log.sell.signal.execute_price - log.sell.signal.parent_order.difference
                        run_up = -(np.min(price) - log.entry_price) / \
                            log.entry_price

                else:
                    returns_diff = (
                        (log.exit_price - log.entry_price) / log.entry_price)
                    # diff of price
                    drawdown = -(np.min(data_low) - log.entry_price) / \
                        log.entry_price
                    run_up = (np.max(data_high) - log.entry_price) / \
                        log.entry_price

                    if 'Trailing_stop' in log.exit_type:
                        price = log.sell.signal.execute_price + log.sell.signal.parent_order.difference
                        run_up = (np.max(price) - log.entry_price) / \
                            log.entry_price

                if drawdown <= 0:
                    drawdown = 0

            log_dict['drawdown'].append(drawdown)
            log_dict['run_up'].append(run_up)
            log_dict['returns_diff'].append(returns_diff)

        return pd.DataFrame(log_dict)

    def trade_analysis(self, full_trade_log: pd.DataFrame=None):
        if full_trade_log:
            OnePyEnvBase.full_trade_log = full_trade_log
        else:
            OnePyEnvBase.full_trade_log = self.get_full_trade_log()

        from OnePy.custom_module.trade_log_analysis import APP
        APP.run_server(debug=False)
