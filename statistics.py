"""
statistics
---------
Calculate trading statistics
"""

# Use future imports for python 3.0 forward compatibility
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Other imports
import pandas as pd
import numpy as np
import operator
import math
import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from numpy.lib.stride_tricks import as_strided


#####################################################################
# CONSTANTS

TRADING_DAYS_PER_YEAR = 252
TRADING_DAYS_PER_MONTH = 20
TRADING_DAYS_PER_WEEK = 5


#####################################################################
# HELPER FUNCTIONS

def _difference_in_years(start, end):
    """ calculate the number of years between two dates """
    diff  = end - start
    diff_in_years = (diff.days + diff.seconds/86400)/365.2425
    return diff_in_years

def _get_trade_bars(dbal):

    l = []
    for i in range(len(tlog.index)):
        if op(tlog['pl_cash'][i], 0):
            entry_date = tlog['entry_date'][i]
            exit_date = tlog['exit_date'][i]
            l.append(len(ts[entry_date:exit_date].index))
    return l

def _get_exit_tlog(tlog):
    return tlog[(tlog['s_type'] == 'EXIT_ALL') | \
                (tlog['s_type'] == 'EXIT_LONG') | \
                (tlog['s_type'] == 'EXIT_SHORT')]

#####################################################################
# OVERALL RESULTS

def beginning_balance(capital):
    return capital

def ending_balance(dbal):
    return dbal[['total']].iat[-1,-1]

def total_net_profit(dbal,capital):
    return dbal[['total']].iat[-1,-1]- capital

def gross_profit(tlog):
    return tlog[tlog['PnL'] > 0].sum()['PnL']

def gross_loss(tlog):
    return tlog[tlog['PnL'] < 0].sum()['PnL']

def profit_and_loss_ratio(tlog):
    if gross_profit(tlog) == 0: return 0
    if gross_loss(tlog) == 0: return 'Never Lose! This is your OnePiece!'
    return gross_profit(tlog) / gross_loss(tlog) * -1

def return_on_initial_capital(dbal, capital):
    return total_net_profit(dbal,capital) / capital * 100

def _cagr(B, A, n):
    """ calculate compound annual growth rate """
    return (math.pow(B / A, 1 / n) - 1) * 100

def annual_return_rate(end_balance, capital, start, end):
    B = end_balance
    A = capital
    n = _difference_in_years(start, end)
    return _cagr(B, A, n)

def trading_period(start, end):
    diff = relativedelta(end, start)
    return '{} years {} months {} days'.format(diff.years, diff.months,
                                               diff.days)

def pct_time_in_market(dbal):
    df = copy.deepcopy(dbal)
    df.drop(df.columns[-5:],1,inplace=True)
    df = df.T
    df = pd.DataFrame(df.sum()).replace(0,float('nan'))
    df.dropna(inplace=True)
    in_market = float(len(df.index))
    total_market = float(len(dbal.index))
    return '%0.2f%%' % (in_market / total_market *100)

#####################################################################
# SUMS
def total_num_trades(tlog):
    return len(tlog.index)

def total_EXIT_trades(ori_tlog):
    ori_tlog = _get_exit_tlog(ori_tlog)
    return len(ori_tlog.index)

def num_winning_trades(tlog):
    return (tlog['PnL'] > 0).sum()

def num_losing_trades(tlog):
    return (tlog['PnL'] < 0).sum()

def num_even_trades(tlog):
    return (tlog['PnL'] == 0).sum()

def pct_profitable_trades(tlog,ori_tlog):
    if total_EXIT_trades(ori_tlog) == 0: return 0
    return '%0.2f%%' % (float(num_winning_trades(tlog)) / \
                        float(total_num_trades(tlog)) * 100)

#####################################################################
# CASH PROFITS AND LOSSES

def avg_profit_per_trade(tlog,ori_tlog,dbal,capital):
    if total_EXIT_trades(ori_tlog) == 0: return 0
    return float(total_net_profit(dbal,capital)) / total_num_trades(tlog)

def avg_profit_per_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return float(gross_profit(tlog)) / num_winning_trades(tlog)

def avg_loss_per_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return float(gross_loss(tlog)) / num_losing_trades(tlog)

def ratio_avg_profit_win_loss(tlog):
    if avg_profit_per_winning_trade(tlog) == 0: return 0
    if avg_loss_per_losing_trade(tlog) == 0: return 1000
    return (avg_profit_per_winning_trade(tlog) /
            avg_loss_per_losing_trade(tlog) * -1)

def largest_profit_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return tlog[tlog['PnL'] > 0].max()['PnL']

def largest_loss_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return tlog[tlog['PnL'] < 0].min()['PnL']

#####################################################################
# POINTS

def num_winning_points(tlog):
    if num_winning_trades(tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return points[points > 0].sum()

def num_losing_points(tlog):
    if num_losing_trades(tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return points[points < 0].sum()

def total_net_points(tlog):
    return num_winning_points(tlog) + num_losing_points(tlog)

def avg_points(tlog,ori_tlog):
    if total_EXIT_trades(ori_tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return points.sum() / len(tlog.index)

def largest_points_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return points.max()

def largest_points_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return points.min()

def avg_pct_gain_points_per_trade(tlog,ori_tlog):
    if total_EXIT_trades(ori_tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    pct = np.average(points) / np.average(_get_exit_tlog(ori_tlog)['price'])
    return '%0.2f%%' % (pct * 100)

def largest_pct_winning_point(tlog):
    if num_winning_trades(tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return '%0.2f%%' % (points.max() * 100)

def largest_pct_losing_point(tlog):
    if num_losing_trades(tlog) == 0: return 0
    points = tlog['PnL']/tlog['qty']
    return '%0.2f%%' % (points.min() * 100)

#####################################################################
# STREAKS

def _subsequence(s, c):
    """
    Takes as parameter list like object s and returns the length of the longest
    subsequence of s constituted only by consecutive character 'c's.
    Example: If the string passed as parameter is "001000111100", and c is '0',
    then the longest subsequence of only '0's has length 3.
    """

    bit = 0        # current element in the sequence
    count = 0      # current length of the sequence of zeros
    maxlen = 0     # temporary value of the maximum length

    for i in range(len(s)):
        bit = s[i]

        if bit == c:            # we have read a new '0'
            count = count + 1   # update the length of the current sequence
            if count > maxlen:  # if necessary, ...
                                # ... update the temporary maximum
                maxlen = count
        else:                   # we have read a 1
            count = 0           # reset the length of the current sequence
    return maxlen

def max_consecutive_winning_periods(tlog,dbal):
    if num_winning_trades(tlog) == 0: return 0
    return _subsequence(dbal['returns'] > 0, True)

def max_consecutive_losing_periods(tlog,dbal):
    if num_losing_trades(tlog) == 0: return 0
    return _subsequence(dbal['returns'] > 0, False)

def periods_winning_trades(tlog,dbal):
    if num_winning_trades(tlog) == 0: return 0
    dbal = dbal['returns']
    return len(dbal[dbal > 0])

def periods_losing_trades(tlog,dbal):
    if num_losing_trades(tlog) == 0: return 0
    dbal = dbal['returns']
    return len(dbal[dbal < 0])

#####################################################################
# DRAWDOWN AND RUNUP

def max_closed_out_drawdown(close):
    """ only compare each point to the previous running peak O(N) """
    running_max = close.expanding().max()
    cur_dd = (close - running_max) / running_max * 100
    dd_max = min(0, cur_dd.min())
    idx = cur_dd.idxmin()

    dd = pd.Series()
    dd['max'] = dd_max
    dd['peak'] = running_max[idx]
    dd['trough'] = close[idx]
    dd['start_date'] = close[close == dd['peak']].index[0].strftime('%Y-%m-%d')
    dd['end_date'] = idx.strftime('%Y-%m-%d')
    close = close[close.index > idx]

    rd_mask = close > dd['peak']
    if rd_mask.any():
        dd['recovery_date'] = \
            close[rd_mask].index[0].strftime('%Y-%m-%d')
    else:
        dd['recovery_date'] = 'Not Recovered Yet'

    return dd

def max_intra_day_drawdown(high, low):
    """ only compare each point to the previous running peak O(N) """
    running_max = high.expanding().max()
    cur_dd = (low - running_max) / running_max * 100
    dd_max = min(0, cur_dd.min())
    idx = cur_dd.idxmin()

    dd = pd.Series()
    dd['max'] = dd_max
    dd['peak'] = running_max[idx]
    dd['trough'] = low[idx]
    dd['start_date'] = high[high == dd['peak']].index[0].strftime('%Y-%m-%d')
    dd['end_date'] = idx.strftime('%Y-%m-%d')
    high = high[high.index > idx]

    rd_mask = high > dd['peak']
    if rd_mask.any():
        dd['recovery_date'] = \
            high[rd_mask].index[0].strftime('%Y-%m-%d')
    return dd

def _windowed_view(x, window_size):
    """Create a 2d windowed view of a 1d array.

    `x` must be a 1d numpy array.

    `numpy.lib.stride_tricks.as_strided` is used to create the view.
    The data is not copied.

    Example:

    >>> x = np.array([1, 2, 3, 4, 5, 6])
    >>> _windowed_view(x, 3)
    array([[1, 2, 3],
           [2, 3, 4],
           [3, 4, 5],
           [4, 5, 6]])
    """
    y = as_strided(x, shape=(x.size - window_size + 1, window_size),
                   strides=(x.strides[0], x.strides[0]))
    return y

def rolling_max_dd(ser, period, min_periods=1):
    """Compute the rolling maximum drawdown of `ser`.

    `ser` must be a Series.
    `min_periods` should satisfy `1 <= min_periods <= window_size`.

    Returns an 1d array with length `len(x) - min_periods + 1`.
    """
    window_size = period + 1
    x = ser.values
    if min_periods < window_size:
        pad = np.empty(window_size - min_periods)
        pad.fill(x[0])
        x = np.concatenate((pad, x))
    y = _windowed_view(x, window_size)
    running_max_y = np.maximum.accumulate(y, axis=1)
    dd = (y - running_max_y) / running_max_y * 100
    rmdd = dd.min(axis=1)
    return pd.Series(data=rmdd, index=ser.index, name=ser.name)

def rolling_max_ru(ser, period, min_periods=1):
    """Compute the rolling maximum runup of `ser`.

    `ser` must be a Series.
    `min_periods` should satisfy `1 <= min_periods <= window_size`.

    Returns an 1d array with length `len(x) - min_periods + 1`.
    """
    window_size = period + 1
    x = ser.values
    if min_periods < window_size:
        pad = np.empty(window_size - min_periods)
        pad.fill(x[0])
        x = np.concatenate((pad, x))
    y = _windowed_view(x, window_size)
    running_min_y = np.minimum.accumulate(y, axis=1)
    ru = (y - running_min_y) / running_min_y * 100
    rmru = ru.max(axis=1)
    return pd.Series(data=rmru, index=ser.index, name=ser.name)

#####################################################################
# PERCENT CHANGE - used to compute several stastics

def pct_change(close, period):
    diff = (close.shift(-period) - close) / close * 100
    diff.dropna(inplace=True)
    return diff

#####################################################################
# RATIOS

def sharpe_ratio(rets, risk_free=0.00, period=TRADING_DAYS_PER_YEAR):
    """
    summary Returns the daily Sharpe ratio of the returns.
    param rets: 1d numpy array or fund list of daily returns (centered on 0)
    param risk_free: risk free returns, default is 0%
    return Sharpe Ratio, computed off daily returns
    """
    dev = np.std(rets, axis=0)
    mean = np.mean(rets, axis=0)
    sharpe = (mean*period - risk_free) / (dev * np.sqrt(period))
    return sharpe

def sortino_ratio(rets, risk_free=0.00, period=TRADING_DAYS_PER_YEAR):
    """
    summary Returns the daily Sortino ratio of the returns.
    param rets: 1d numpy array or fund list of daily returns (centered on 0)
    param risk_free: risk free return, default is 0%
    return Sortino Ratio, computed off daily returns
    """
    mean = np.mean(rets, axis=0)
    negative_rets = rets[rets < 0]
    dev = np.std(negative_rets, axis=0)
    sortino = (mean*period - risk_free) / (dev * np.sqrt(period))
    return sortino

#####################################################################
# STATS - this is the primary call used to generate the results

def stats(tlog,ori_tlog, dbal, start, end, capital):
    """
    Compute trading stats
    Parameters
    ----------
    ts : Dataframe
        Time series of security prices (date, high, low, close, volume,
        adj_close)
    tlog : Dataframe
        Trade log (entry_date, entry_price, long_short, qty,
        exit_date, exit_price, pl_points, pl_cash, cumul_total)
    dbal : Dataframe
        Daily Balance (date, high, low, close)
    start : datetime
        date of first buy
    end : datetime
        date of last sell
    capital : float
        starting capital

    Examples
    --------

    Returns
    -------
    stats : Series of stats
    """

    stats = pd.Series()

    # OVERALL RESULTS
    stats['start'] = start.strftime('%Y-%m-%d')
    stats['end'] = end.strftime('%Y-%m-%d')
    stats['beginning_balance'] = beginning_balance(capital)
    stats['ending_balance'] = ending_balance(dbal)
    stats['total_net_profit'] = total_net_profit(dbal,capital)
    stats['gross_profit'] = gross_profit(tlog)
    stats['gross_loss'] = gross_loss(tlog)
    stats['P/L'] = profit_and_loss_ratio(tlog)
    stats['return_on_initial_capital'] = \
        return_on_initial_capital(tlog, capital)
    cagr = annual_return_rate(ending_balance(dbal), capital, start, end)
    stats['annual_return_rate'] = cagr
    stats['trading_period'] = trading_period(start, end)
    stats['pct_time_in_market'] = pct_time_in_market(dbal)

    # SUMS
    stats['total_num_trades'] = total_num_trades(tlog)
    stats['total_EXIT_trades'] = total_EXIT_trades(ori_tlog)
    stats['num_winning_trades'] = num_winning_trades(tlog)
    stats['num_losing_trades'] = num_losing_trades(tlog)
    stats['num_even_trades'] = num_even_trades(tlog)
    stats['pct_profitable_trades'] = pct_profitable_trades(tlog,ori_tlog)

    # CASH PROFITS AND LOSSES
    stats['avg_profit_per_trade'] = avg_profit_per_trade(tlog,ori_tlog,dbal,capital)
    stats['avg_profit_per_winning_trade'] = avg_profit_per_winning_trade(tlog)
    stats['avg_loss_per_losing_trade'] = avg_loss_per_losing_trade(tlog)
    stats['ratio_avg_profit_win_loss'] = ratio_avg_profit_win_loss(tlog)
    stats['largest_profit_winning_trade'] = largest_profit_winning_trade(tlog)
    stats['largest_loss_losing_trade'] = largest_loss_losing_trade(tlog)

    # POINTS
    stats['num_winning_points'] = num_winning_points(tlog)
    stats['num_losing_points'] = num_losing_points(tlog)
    stats['total_net_points'] = total_net_points(tlog)
    stats['avg_points'] = avg_points(tlog,ori_tlog)
    stats['largest_points_winning_trade'] = largest_points_winning_trade(tlog)
    stats['largest_points_losing_trade'] = largest_points_losing_trade(tlog)
    stats['avg_pct_gain_per_trade'] = avg_pct_gain_points_per_trade(tlog,ori_tlog)
    stats['largest_pct_winning_trade'] = largest_pct_winning_point(tlog)
    stats['largest_pct_losing_trade'] = largest_pct_losing_point(tlog)

    # STREAKS
    stats['max_consecutive_winning_periods'] = \
        max_consecutive_winning_periods(tlog,dbal)
    stats['max_consecutive_losing_periods'] = \
        max_consecutive_losing_periods(tlog,dbal)
    stats['periods_winning_trades'] = \
        periods_winning_trades(tlog,dbal)
    stats['periods_losing_trades'] = periods_losing_trades(tlog,dbal)
    #
    # # DRAWDOWN
    # dd = max_closed_out_drawdown(dbal['close'])
    # stats['max_closed_out_drawdown'] = dd['max']
    # stats['max_closed_out_drawdown_start_date'] = dd['start_date']
    # stats['max_closed_out_drawdown_end_date'] = dd['end_date']
    # stats['max_closed_out_drawdown_recovery_date'] = dd['recovery_date']
    # stats['drawdown_recovery'] = _difference_in_years(
    #     datetime.strptime(dd['start_date'], '%Y-%m-%d'),
    #     datetime.strptime(dd['end_date'], '%Y-%m-%d')) *-1
    # stats['drawdown_annualized_return'] = dd['max'] / cagr
    # dd = max_intra_day_drawdown(dbal['high'], dbal['low'])
    # stats['max_intra_day_drawdown'] = dd['max']
    # dd = rolling_max_dd(dbal['close'], TRADING_DAYS_PER_YEAR)
    # stats['avg_yearly_closed_out_drawdown'] = np.average(dd)
    # stats['max_yearly_closed_out_drawdown'] = min(dd)
    # dd = rolling_max_dd(dbal['close'], TRADING_DAYS_PER_MONTH)
    # stats['avg_monthly_closed_out_drawdown'] = np.average(dd)
    # stats['max_monthly_closed_out_drawdown'] = min(dd)
    # dd = rolling_max_dd(dbal['close'], TRADING_DAYS_PER_WEEK)
    # stats['avg_weekly_closed_out_drawdown'] = np.average(dd)
    # stats['max_weekly_closed_out_drawdown'] = min(dd)
    #
    # # RUNUP
    # ru = rolling_max_ru(dbal['close'], TRADING_DAYS_PER_YEAR)
    # stats['avg_yearly_closed_out_runup'] = np.average(ru)
    # stats['max_yearly_closed_out_runup'] = ru.max()
    # ru = rolling_max_ru(dbal['close'], TRADING_DAYS_PER_MONTH)
    # stats['avg_monthly_closed_out_runup'] = np.average(ru)
    # stats['max_monthly_closed_out_runup'] = max(ru)
    # ru = rolling_max_ru(dbal['close'], TRADING_DAYS_PER_WEEK)
    # stats['avg_weekly_closed_out_runup'] = np.average(ru)
    # stats['max_weekly_closed_out_runup'] = max(ru)
    #
    # # PERCENT CHANGE
    # pc = pct_change(dbal['close'], TRADING_DAYS_PER_YEAR)
    # stats['pct_profitable_years'] = (pc > 0).sum() / len(pc) * 100
    # stats['best_year'] = pc.max()
    # stats['worst_year'] = pc.min()
    # stats['avg_year'] = np.average(pc)
    # stats['annual_std'] = pc.std()
    # pc = pct_change(dbal['close'], TRADING_DAYS_PER_MONTH)
    # stats['pct_profitable_months'] = (pc > 0).sum() / len(pc) * 100
    # stats['best_month'] = pc.max()
    # stats['worst_month'] = pc.min()
    # stats['avg_month'] = np.average(pc)
    # stats['monthly_std'] = pc.std()
    # pc = pct_change(dbal['close'], TRADING_DAYS_PER_WEEK)
    # stats['pct_profitable_weeks'] = (pc > 0).sum() / len(pc) * 100
    # stats['best_week'] = pc.max()
    # stats['worst_week'] = pc.min()
    # stats['avg_week'] = np.average(pc)
    # stats['weekly_std'] = pc.std()
    #
    # # RATIOS
    # stats['sharpe_ratio'] = sharpe_ratio(dbal['close'].pct_change())
    # stats['sortino_ratio'] = sortino_ratio(dbal['close'].pct_change())
    return stats

#####################################################################
# SUMMARY - stats() must be called before calling any of these functions

def summary(stats, *metrics):
    """ Returns stats summary in a DataFrame.
        stats() must be called before calling this function """
    index = []
    columns = ['strategy']
    data = []
    # add metrics
    for metric in metrics:
        index.append(metric)
        data.append(stats[metric])

    df = pd.DataFrame(data, columns=columns, index=index)
    return df

def summary2(stats, benchmark_stats, *metrics):
    """ Returns stats with benchmark summary in a DataFrame.
        stats() must be called before calling this function """
    index = []
    columns = ['strategy', 'benchmark']
    data = []
    # add metrics
    for metric in metrics:
        index.append(metric)
        data.append((stats[metric], benchmark_stats[metric]))

    df = pd.DataFrame(data, columns=columns, index=index)
    return df

def summary3(stats, benchmark_stats, *extras):
    """ Returns stats with benchmark summary in a DataFrame.
        stats() must be called before calling this function
        *extras: extra metrics """
    index = ['annual_return_rate',
             'max_closed_out_drawdown',
             'drawdown_annualized_return',
             'pct_profitable_months',
             'best_month',
             'worst_month',
             'sharpe_ratio',
             'sortino_ratio']
    columns = ['strategy', 'benchmark']
    data = [(stats['annual_return_rate'],
             benchmark_stats['annual_return_rate']),
            (stats['max_closed_out_drawdown'],
             benchmark_stats['max_closed_out_drawdown']),
            (stats['drawdown_annualized_return'],
             benchmark_stats['drawdown_annualized_return']),
            (stats['pct_profitable_months'],
             benchmark_stats['pct_profitable_months']),
            (stats['best_month'],
             benchmark_stats['best_month']),
            (stats['worst_month'],
             benchmark_stats['worst_month']),
            (stats['sharpe_ratio'],
             benchmark_stats['sharpe_ratio']),
            (stats['sortino_ratio'],
             benchmark_stats['sortino_ratio'])]
    # add extra metrics
    for extra in extras:
        index.append(extra)
        data.append((stats[extra], benchmark_stats[extra]))

    df = pd.DataFrame(data, columns=columns, index=index)
    return df
