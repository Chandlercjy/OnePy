
from OnePy.builtin_module.backtest_stock.stock_broker import StockBroker
from OnePy.constants import ActionType
from OnePy.sys_module.components.order_checker import SubmitOrderChecker
from OnePy.sys_module.components.order_generator import OrderGenerator
from setting_for_test import (END, FREQUENCY, INSTRUMENT, START, TICKER,
                              global_setting)


def test_submit_order_checker():
    go = global_setting()
    strategy = go.env.strategies['DemoStrategy']
    go.market_maker.update_market()
    order_generator = OrderGenerator()
    order_checker = SubmitOrderChecker(StockBroker._required_cash_func)

    NEXT_OPEN = 10

    def settle_next_open():
        go.env.initialize_env()
        go.market_maker.initialize()
        go.market_maker.update_market()
        go.env.execute_on_close_or_next_open = 'open'
        go.env.feeds[TICKER].next_ohlc['open'] = NEXT_OPEN

    # 测试 缺少position
    settle_next_open()
    strategy.sell(100, TICKER)
    strategy.cover(100, TICKER)
    order_generator.run()
    order_checker.run()
    assert go.env.orders_mkt_submitted_cur == []

    # 测试 缺少cash
    settle_next_open()
    assert TICKER in go.env.tickers
    strategy.buy(100, TICKER)
    strategy.buy(100, TICKER)
    go.env.recorder.cash[-1]['value'] = NEXT_OPEN*100
    order_generator.run()
    order_checker.run()
    assert len(go.env.orders_mkt_submitted_cur) == 1

    settle_next_open()
    strategy.buy(100, TICKER)
    strategy.buy(100, TICKER)
    go.env.recorder.cash[-1]['value'] = NEXT_OPEN*100 - 1
    order_generator.run()
    order_checker.run()
    assert go.env.orders_mkt_submitted_cur == []

    settle_next_open()
    strategy.buy(100, TICKER)
    strategy.buy(100, TICKER)
    go.env.recorder.cash[-1]['value'] = NEXT_OPEN*100 + 1
    order_generator.run()
    order_checker.run()
    assert len(go.env.orders_mkt_submitted_cur) == 1

    # 测试 partial 成交
    settle_next_open()
    strategy.sell(100, TICKER)
    strategy.cover(100, TICKER)
    long_po = go.env.recorder.position.data[f'{TICKER}_long'][-1]['value'] = 30
    short_po = go.env.recorder.position.data[f'{TICKER}_short'][-1]['value'] = 40
    order_generator.run()
    order_checker.run()
    assert len(go.env.orders_mkt_submitted_cur) == 2

    for order in go.env.orders_mkt_submitted_cur:
        if order.action_type == ActionType.Sell:
            assert order.size == long_po
        elif order.action_type == ActionType.Cover:
            assert order.size == short_po
        else:
            raise Exception("This can't be raised")


if __name__ == "__main__":
    test_submit_order_checker()
