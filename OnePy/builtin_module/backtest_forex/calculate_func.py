
def dollar_per_pips(ticker, cur_price):
    """外汇专用"""

    if ticker[:3] == 'USD':
        return 10/cur_price
    elif ticker[-3:] == 'USD':
        return 10
    else:
        raise Exception("Could only backtest in USD currency pairs.")


def market_value_multiplayer(ticker, cur_price):
    """外汇专用"""

    if ticker[:3] == 'USD':
        return 1
    elif ticker[-3:] == 'USD':
        return cur_price
    else:
        raise Exception("Could only backtest in USD currency pairs.")
