#coding=utf8
"""
statistics
---------
Calculate trading statistics
"""

# Other imports
import pandas as pd
import numpy as np
import operator
import math
import funcy as fy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from numpy.lib.stride_tricks import as_strided
from collections import OrderedDict

#####################################################################
# CONSTANTS

TRADING_DAYS_PER_YEAR = 252
TRADING_DAYS_PER_MONTH = 20
TRADING_DAYS_PER_WEEK = 5


#####################################################################
# HELPER FUNCTIONS

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    ratio = np.sqrt(periods) * (np.mean(returns)) / np.std(returns)
    return ratio[0]


def create_drawdowns(equity_curve):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    # Then create the drawdown and duration series
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx)
    duration = pd.Series(index = eq_idx)

    # Loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve[t])
        hwm.append(cur_hwm)
        drawdown[t]= hwm[t] - equity_curve[t]
        duration[t]= 0 if drawdown[t] == 0 else duration[t-1] + 1
    return round(drawdown.max(),5), round(duration.max(),3)



def create_trade_log(completed_list,target,commtype,mult):
    tlog_list = []
    for i in completed_list:
        f = i[1]
        if commtype is 'FIX':
            if target is 'Futures':
                comm = f.commission*f.direction
            else:
                comm = f.commission*f.direction/mult
        elif commtype is 'PCT':
            if target is 'Futures':
                comm = 1.0 + f.commission*f.direction*mult
            else:
                comm = 1.0 + f.commission*f.direction
        d = {}
        d['entry_date'] = i[0].date
        d['entry_price'] = i[0].price
        d['signal_type'] = i[0].signal_type
        d['size'] = round(min(i[0].size,i[1].size),3)
        d['exit_date'] = i[1].date
        d['exit_price'] = i[1].price
        d['pl_points'] = i[1].price - i[0].price
        d['execute_type'] = i[1].executetype

        if commtype is 'FIX':
            d['re_profit'] =  (i[1].price-(i[0].price-comm)) * d['size'] * mult * i[0].direction
        elif commtype is 'PCT':
            d['re_profit'] =  (i[1].price*comm-i[0].price) * d['size'] * mult * i[0].direction
        tlog_list.append(d)

    df = pd.DataFrame(tlog_list)
    df['cumul_total'] = df[['re_profit']].cumsum()
    return df[['entry_date','entry_price','signal_type','size','exit_date',
             'exit_price','execute_type','pl_points','re_profit','cumul_total']]





def _difference_in_years(start, end):
    """ calculate the number of years between two dates """
    diff  = end - start
    diff_in_years = (diff.days + diff.seconds/86400)/365.2425
    return diff_in_years

def _get_trade_bars(ts, tlog, op):

    l = []
    for i in range(len(tlog.index)):
        if op(tlog['re_profit'][i], 0):
            entry_date = tlog['entry_date'][i]
            exit_date = tlog['exit_date'][i]
            l.append(len(ts[entry_date:exit_date].index))
    return l

#####################################################################
# OVERALL RESULTS

def beginning_balance(capital):
    return capital

def ending_balance(dbal):
    return dbal.iloc[-1]['total']

def total_net_profit(tlog):
    return tlog.iloc[-1]['cumul_total']

def gross_profit(tlog):
    return tlog[tlog['re_profit'] > 0].sum()['re_profit']

def gross_loss(tlog):
    return tlog[tlog['re_profit'] < 0].sum()['re_profit']

def profit_factor(tlog):
    if gross_profit(tlog) == 0: return 0
    if gross_loss(tlog) == 0: return 1000
    return gross_profit(tlog) / gross_loss(tlog) * -1

def return_on_initial_capital(tlog, capital):
    return total_net_profit(tlog) / capital * 100

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

def _true_func(arg1, arg2):
    return True

def _total_days_in_market(ts, tlog):
    l = _get_trade_bars(ts, tlog, _true_func)
    return sum(l)

def pct_time_in_market(ts, tlog, start, end):
    return _total_days_in_market(ts, tlog) / len(ts[start:end].index) * 100

#####################################################################
# SUMS

def total_num_trades(tlog):
    return len(tlog.index)

def num_winning_trades(tlog):
    return (tlog['re_profit'] > 0).sum()

def num_losing_trades(tlog):
    return (tlog['re_profit'] < 0).sum()

def num_even_trades(tlog):
    return (tlog['re_profit'] == 0).sum()

def pct_profitable_trades(tlog):
    if total_num_trades(tlog) == 0: return 0
    return num_winning_trades(tlog) / total_num_trades(tlog) * 100

#####################################################################
# CASH PROFITS AND LOSSES

def avg_profit_per_trade(tlog):
    if total_num_trades(tlog) == 0: return 0
    return total_net_profit(tlog) / total_num_trades(tlog)

def avg_profit_per_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return gross_profit(tlog) / num_winning_trades(tlog)

def avg_loss_per_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return gross_loss(tlog) / num_losing_trades(tlog)

def ratio_avg_profit_win_loss(tlog):
    if avg_profit_per_winning_trade(tlog) == 0: return 0
    if avg_loss_per_losing_trade(tlog) == 0: return 1000
    return (avg_profit_per_winning_trade(tlog) /
            avg_loss_per_losing_trade(tlog) * -1)

def largest_profit_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return tlog[tlog['re_profit'] > 0].max()['re_profit']

def largest_loss_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return tlog[tlog['re_profit'] < 0].min()['re_profit']

#####################################################################
# POINTS

def num_winning_points(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return tlog[tlog['pl_points'] > 0].sum()['pl_points']

def num_losing_points(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return tlog[tlog['pl_points'] < 0].sum()['pl_points']

def total_net_points(tlog):
    return num_winning_points(tlog) + num_losing_points(tlog)

def avg_points(tlog):
    if total_num_trades(tlog) == 0: return 0
    return tlog['pl_points'].sum() / len(tlog.index)

def largest_points_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return tlog[tlog['pl_points'] > 0].max()['pl_points']

def largest_points_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return tlog[tlog['pl_points'] < 0].min()['pl_points']

def avg_pct_gain_per_trade(tlog):
    if total_num_trades(tlog) == 0: return 0
    df = tlog['pl_points'] / tlog['entry_price']
    return np.average(df) * 100

def largest_pct_winning_trade(tlog):
    if num_winning_trades(tlog) == 0: return 0
    df = tlog[tlog['pl_points'] > 0]
    df = df['pl_points'] / df['entry_price']
    return df.max() * 100

def largest_pct_losing_trade(tlog):
    if num_losing_trades(tlog) == 0: return 0
    df = tlog[tlog['pl_points'] < 0]
    df = df['pl_points'] / df['entry_price']
    return df.min() * 100

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

def max_consecutive_winning_trades(tlog):
    if num_winning_trades(tlog) == 0: return 0
    return _subsequence(tlog['re_profit'] > 0, True)

def max_consecutive_losing_trades(tlog):
    if num_losing_trades(tlog) == 0: return 0
    return _subsequence(tlog['re_profit'] > 0, False)

def avg_bars_winning_trades(ts, tlog):
    if num_winning_trades(tlog) == 0: return 0
    return np.average(_get_trade_bars(ts, tlog, operator.gt))

def avg_bars_losing_trades(ts, tlog):
    if num_losing_trades(tlog) == 0: return 0
    return np.average(_get_trade_bars(ts, tlog, operator.lt))

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
    dd['start_date'] = close[close == dd['peak']].index[0].strftime("%Y-%m-%d %H:%M:%S")
    dd['end_date'] = idx.strftime("%Y-%m-%d %H:%M:%S")
    close = close[close.index > idx]

    rd_mask = close > dd['peak']
    if rd_mask.any():
        dd['recovery_date'] = \
            close[rd_mask].index[0].strftime("%Y-%m-%d %H:%M:%S")
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
    dd['start_date'] = high[high == dd['peak']].index[0].strftime("%Y-%m-%d %H:%M:%S")
    dd['end_date'] = idx.strftime("%Y-%m-%d %H:%M:%S")
    high = high[high.index > idx]

    rd_mask = high > dd['peak']
    if rd_mask.any():
        dd['recovery_date'] = \
            high[rd_mask].index[0].strftime("%Y-%m-%d %H:%M:%S")
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

def stats(ts, tlog, dbal, start, end, capital):
    """
    Compute trading stats
    Parameters
    ----------
    ts : Dataframe
        Time series of security prices (date, high, low, close, volume,
        adj_close)
    tlog : Dataframe
        Trade log (entry_date, entry_price, long_short, qty,
        exit_date, exit_price, pl_points, re_profit, cumul_total)
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

    stats = OrderedDict()

    # OVERALL RESULTS
    stats['start'] = start.strftime("%Y-%m-%d %H:%M:%S")
    stats['end'] = end.strftime("%Y-%m-%d %H:%M:%S")
    stats['beginning_balance'] = beginning_balance(capital)
    stats['ending_balance'] = ending_balance(dbal)
    stats['unrealized_profit'] = \
        ending_balance(dbal) - total_net_profit(tlog) - beginning_balance(capital)
    stats['total_net_profit'] = total_net_profit(tlog)
    stats['gross_profit'] = gross_profit(tlog)
    stats['gross_loss'] = gross_loss(tlog)
    stats['profit_factor'] = profit_factor(tlog)
    stats['return_on_initial_capital'] = \
        return_on_initial_capital(tlog, capital)
    cagr = annual_return_rate(dbal['total'][-1], capital, start, end)
    stats['annual_return_rate'] = cagr
    stats['trading_period'] = trading_period(start, end)
    stats['pct_time_in_market'] = \
        pct_time_in_market(ts, tlog, start, end)

    # SUMS
    stats['total_num_trades'] = total_num_trades(tlog)
    stats['num_winning_trades'] = num_winning_trades(tlog)
    stats['num_losing_trades'] = num_losing_trades(tlog)
    stats['num_even_trades'] = num_even_trades(tlog)
    stats['pct_profitable_trades'] = pct_profitable_trades(tlog)

    # CASH PROFITS AND LOSSES
    stats['avg_profit_per_trade'] = avg_profit_per_trade(tlog)
    stats['avg_profit_per_winning_trade'] = avg_profit_per_winning_trade(tlog)
    stats['avg_loss_per_losing_trade'] = avg_loss_per_losing_trade(tlog)
    stats['ratio_avg_profit_win_loss'] = ratio_avg_profit_win_loss(tlog)
    stats['largest_profit_winning_trade'] = largest_profit_winning_trade(tlog)
    stats['largest_loss_losing_trade'] = largest_loss_losing_trade(tlog)

    # POINTS
    stats['num_winning_points'] = num_winning_points(tlog)
    stats['num_losing_points'] = num_losing_points(tlog)
    stats['total_net_points'] = total_net_points(tlog)
    stats['avg_points'] = avg_points(tlog)
    stats['largest_points_winning_trade'] = largest_points_winning_trade(tlog)
    stats['largest_points_losing_trade'] = largest_points_losing_trade(tlog)
    stats['avg_pct_gain_per_trade'] = avg_pct_gain_per_trade(tlog)
    stats['largest_pct_winning_trade'] = largest_pct_winning_trade(tlog)
    stats['largest_pct_losing_trade'] = largest_pct_losing_trade(tlog)

    # STREAKS
    stats['max_consecutive_winning_trades'] = \
        max_consecutive_winning_trades(tlog)
    stats['max_consecutive_losing_trades'] = \
        max_consecutive_losing_trades(tlog)
    stats['avg_bars_winning_trades'] = \
        avg_bars_winning_trades(ts, tlog)
    stats['avg_bars_losing_trades'] = avg_bars_losing_trades(ts, tlog)

    # DRAWDOWN
    dd = max_closed_out_drawdown(dbal['total'])
    stats['max_closed_out_drawdown'] = dd['max']
    stats['max_closed_out_drawdown_start_date'] = dd['start_date']
    stats['max_closed_out_drawdown_end_date'] = dd['end_date']
    stats['max_closed_out_drawdown_recovery_date'] = dd['recovery_date']
    stats['drawdown_recovery'] = _difference_in_years(
        datetime.strptime(dd['start_date'], "%Y-%m-%d %H:%M:%S"),
        datetime.strptime(dd['end_date'], "%Y-%m-%d %H:%M:%S")) *-1
    stats['drawdown_annualized_return'] = dd['max'] / cagr
    dd = max_intra_day_drawdown(dbal['total_high'], dbal['total_low'])
    stats['max_intra_day_drawdown'] = dd['max']
    dd = rolling_max_dd(dbal['total'], TRADING_DAYS_PER_YEAR)
    stats['avg_yearly_closed_out_drawdown'] = np.average(dd)
    stats['max_yearly_closed_out_drawdown'] = min(dd)
    dd = rolling_max_dd(dbal['total'], TRADING_DAYS_PER_MONTH)
    stats['avg_monthly_closed_out_drawdown'] = np.average(dd)
    stats['max_monthly_closed_out_drawdown'] = min(dd)
    dd = rolling_max_dd(dbal['total'], TRADING_DAYS_PER_WEEK)
    stats['avg_weekly_closed_out_drawdown'] = np.average(dd)
    stats['max_weekly_closed_out_drawdown'] = min(dd)

    # RUNUP
    ru = rolling_max_ru(dbal['total'], TRADING_DAYS_PER_YEAR)
    stats['avg_yearly_closed_out_runup'] = np.average(ru)
    stats['max_yearly_closed_out_runup'] = ru.max()
    ru = rolling_max_ru(dbal['total'], TRADING_DAYS_PER_MONTH)
    stats['avg_monthly_closed_out_runup'] = np.average(ru)
    stats['max_monthly_closed_out_runup'] = max(ru)
    ru = rolling_max_ru(dbal['total'], TRADING_DAYS_PER_WEEK)
    stats['avg_weekly_closed_out_runup'] = np.average(ru)
    stats['max_weekly_closed_out_runup'] = max(ru)

    # PERCENT CHANGE
    pc = pct_change(dbal['total'], TRADING_DAYS_PER_YEAR)
    stats['pct_profitable_years'] = (pc > 0).sum() / len(pc) * 100
    stats['best_year'] = pc.max()
    stats['worst_year'] = pc.min()
    stats['avg_year'] = np.average(pc)
    stats['annual_std'] = pc.std()
    pc = pct_change(dbal['total'], TRADING_DAYS_PER_MONTH)
    stats['pct_profitable_months'] = (pc > 0).sum() / len(pc) * 100
    stats['best_month'] = pc.max()
    stats['worst_month'] = pc.min()
    stats['avg_month'] = np.average(pc)
    stats['monthly_std'] = pc.std()
    pc = pct_change(dbal['total'], TRADING_DAYS_PER_WEEK)
    stats['pct_profitable_weeks'] = (pc > 0).sum() / len(pc) * 100
    stats['best_week'] = pc.max()
    stats['worst_week'] = pc.min()
    stats['avg_week'] = np.average(pc)
    stats['weekly_std'] = pc.std()

    # RATIOS
    stats['sharpe_ratio'] = sharpe_ratio(dbal['total'].pct_change())
    stats['sortino_ratio'] = sortino_ratio(dbal['total'].pct_change())

    for i,j in stats.items():
        if type(j) is not str:
            stats[i] = round(j,3)

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
