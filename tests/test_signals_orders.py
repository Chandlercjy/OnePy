import OnePy.sys_module.models.orders.general_order as geno
from OnePy.constants import ActionType
from OnePy.sys_module.components.order_generator import OrderGenerator
from OnePy.sys_module.components.signal_generator import SignalGenerator
from OnePy.sys_module.models.signals import Signal
from setting_for_test import TICKER, global_setting, set_easy_context


def test_signals_orders():
    go = global_setting()
    strategy = go.env.strategies['DemoStrategy']
    go.market_maker.update_market()
    order_generator = OrderGenerator()
    go.env.execute_on_close_or_next_open = 'open'
    go.env.is_save_original = True

    CLOSE = go.env.feeds[TICKER].current_ohlc['close'] = 11
    HIGH = go.env.feeds[TICKER].current_ohlc['high'] = 20
    LOW = go.env.feeds[TICKER].current_ohlc['low'] = 5
    NEXT_OPEN = go.env.feeds[TICKER].next_ohlc['open'] = 10

    def test_buy(param_dict: dict, pct: bool):

        go.env.initialize_env()
        signal = strategy.buy(
            100, TICKER, **param_dict)

        assert signal in go.env.signals_normal
        assert signal in go.env.signals_normal_cur
        assert signal.action_type == ActionType.Buy

        order_generator.run()
        mkt_order = go.env.orders_mkt_normal_cur[0]
        assert mkt_order.signal is signal
        assert mkt_order.is_pure() is False
        assert mkt_order.first_cur_price == mkt_order.execute_price == NEXT_OPEN
        assert isinstance(mkt_order.signal, Signal)
        pending_orders = go.env.orders_child_of_mkt_dict[mkt_order.mkt_id]

        for order in pending_orders:
            assert order.action_type == ActionType.Sell

            if isinstance(order, geno.StopSellOrder):
                stop_sell = order
            elif isinstance(order, geno.LimitSellOrder):
                limit_sell = order
            elif isinstance(order, geno.TrailingStopSellOrder):
                trailingstop_sell = order
            else:
                raise Exception("This can't be raised")

        assert stop_sell.signal == limit_sell.signal == trailingstop_sell.signal
        assert stop_sell.mkt_id == limit_sell.mkt_id == trailingstop_sell.mkt_id

        if pct:
            assert stop_sell.trigger_key == 'stoploss_pct'
            assert limit_sell.trigger_key == 'takeprofit_pct'
            assert trailingstop_sell.trigger_key == 'trailingstop_pct'
            assert stop_sell.target_price == round(NEXT_OPEN*0.9, 3)
            assert limit_sell.target_price == round(NEXT_OPEN*1.1, 3)
            assert trailingstop_sell.initialize_latest_target_price() == round(NEXT_OPEN*0.9, 3)
            assert NEXT_OPEN*0.9 <= trailingstop_sell.target_price <= HIGH - NEXT_OPEN*0.1
        else:
            assert stop_sell.trigger_key == 'stoploss'
            assert limit_sell.trigger_key == 'takeprofit'
            assert trailingstop_sell.trigger_key == 'trailingstop'
            assert stop_sell.target_price == NEXT_OPEN - 10/100
            assert limit_sell.target_price == NEXT_OPEN + 10/100
            assert trailingstop_sell.initialize_latest_target_price() == NEXT_OPEN - 10/100
            assert NEXT_OPEN-10/100 <= trailingstop_sell.target_price <= HIGH - 10/100

    def test_short(param_dict: dict, pct: bool):

        go.env.initialize_env()
        signal = strategy.short(
            100, TICKER, **param_dict)

        assert signal in go.env.signals_normal
        assert signal in go.env.signals_normal_cur
        assert signal.action_type == ActionType.Short

        order_generator.run()
        mkt_order = go.env.orders_mkt_normal_cur[0]
        assert mkt_order.signal is signal
        assert mkt_order.is_pure() is False
        assert mkt_order.first_cur_price == mkt_order.execute_price == NEXT_OPEN
        assert isinstance(mkt_order.signal, Signal)
        pending_orders = go.env.orders_child_of_mkt_dict[mkt_order.mkt_id]

        for order in pending_orders:
            assert order.action_type == ActionType.Cover

            if isinstance(order, geno.StopCoverOrder):
                stop_cover_short = order
            elif isinstance(order, geno.LimitCoverOrder):
                limit_cover_short = order
            elif isinstance(order, geno.TrailingStopCoverOrder):
                trailingstop_cover_short = order
            else:
                raise Exception("This can't be raised")

        assert stop_cover_short.signal == limit_cover_short.signal == trailingstop_cover_short.signal
        assert stop_cover_short.mkt_id == limit_cover_short.mkt_id == trailingstop_cover_short.mkt_id

        if pct:
            assert stop_cover_short.trigger_key == 'stoploss_pct'
            assert limit_cover_short.trigger_key == 'takeprofit_pct'
            assert trailingstop_cover_short.trigger_key == 'trailingstop_pct'
            assert stop_cover_short.target_price == round(NEXT_OPEN*1.1, 3)
            assert limit_cover_short.target_price == round(NEXT_OPEN*0.9, 3)
            assert trailingstop_cover_short.initialize_latest_target_price() == round(NEXT_OPEN*1.1, 3)

            if go.env.instrument == 'A_shares':  # A股要做跳高跳空成交处理
                OPEN = go.env.feeds[TICKER].current_ohlc['open'] = 15
                assert trailingstop_cover_short.target_price == OPEN
            else:
                assert LOW+NEXT_OPEN*0.1 <= trailingstop_cover_short.target_price <= NEXT_OPEN*1.1
        else:

            assert stop_cover_short.trigger_key == 'stoploss'
            assert limit_cover_short.trigger_key == 'takeprofit'
            assert trailingstop_cover_short.trigger_key == 'trailingstop'
            assert stop_cover_short.target_price == NEXT_OPEN + 10/100
            assert limit_cover_short.target_price == NEXT_OPEN - 10/100
            assert trailingstop_cover_short.initialize_latest_target_price() == NEXT_OPEN + \
                10/100

            if go.env.instrument == 'A_shares':  # A股要做跳高跳空成交处理
                OPEN = go.env.feeds[TICKER].current_ohlc['open'] = 15
                assert trailingstop_cover_short.target_price == OPEN
            else:
                assert LOW + 10/100 <= trailingstop_cover_short.target_price <= NEXT_OPEN + 10/100

    test_buy(dict(takeprofit=10, stoploss=10,  # 测试 Buy
                  trailingstop=10), pct=False)

    test_buy(dict(takeprofit_pct=0.1, stoploss_pct=0.1,  # 测试 Buy  指令,带pct
                  trailingstop_pct=0.1), pct=True)

    test_short(dict(takeprofit=10, stoploss=10,  # 测试 Short
                    trailingstop=10), pct=False)

    test_short(dict(takeprofit_pct=0.1, stoploss_pct=0.1,  # 测试 Short 指令,带pct
                    trailingstop_pct=0.1), pct=True)

    # 测试Sell
    go.env.initialize_env()
    signal = strategy.sell(100, TICKER)
    order_generator.run()
    mkt_order = go.env.orders_mkt_normal_cur[0]
    assert mkt_order.execute_price == NEXT_OPEN

    # 测试 Cover
    go.env.initialize_env()
    signal = strategy.cover(100, TICKER)
    order_generator.run()
    mkt_order = go.env.orders_mkt_normal_cur[0]
    assert mkt_order.execute_price == NEXT_OPEN

    def func_test_pending_order(order_func, order_class, param_dict, target_price):
        go.env.initialize_env()
        signal = order_func(100, TICKER, **param_dict)
        assert signal.price == target_price
        order_generator.run()
        pending_order = go.env.orders_pending[0]
        assert isinstance(pending_order, order_class) is True
        assert pending_order.target_price == round(signal.price, 3)

    # 测试挂单 Buy
    func_test_pending_order(strategy.buy, geno.StopBuyOrder,
                            dict(price_pct=0.01), CLOSE*1.01)
    func_test_pending_order(strategy.buy, geno.LimitBuyOrder,
                            dict(price_pct=-0.01), CLOSE*0.99)
    func_test_pending_order(strategy.buy, geno.StopBuyOrder,
                            dict(price=CLOSE+1), CLOSE+1)
    func_test_pending_order(strategy.buy, geno.LimitBuyOrder,
                            dict(price=CLOSE-1), CLOSE-1)

    # 测试挂单Sell
    func_test_pending_order(strategy.sell, geno.LimitSellOrder,
                            dict(price_pct=0.01), CLOSE*1.01)
    func_test_pending_order(strategy.sell, geno.StopSellOrder,
                            dict(price_pct=-0.01), CLOSE*0.99)
    func_test_pending_order(strategy.sell, geno.LimitSellOrder,
                            dict(price=CLOSE+1), CLOSE+1)
    func_test_pending_order(strategy.sell, geno.StopSellOrder,
                            dict(price=CLOSE-1), CLOSE-1)

    # 测试挂单 Short
    func_test_pending_order(strategy.short, geno.LimitShortOrder,
                            dict(price_pct=0.01), CLOSE*1.01)
    func_test_pending_order(strategy.short, geno.StopShortOrder,
                            dict(price_pct=-0.01), CLOSE*0.99)
    func_test_pending_order(strategy.short, geno.LimitShortOrder,
                            dict(price=CLOSE+1), CLOSE+1)
    func_test_pending_order(strategy.short, geno.StopShortOrder,
                            dict(price=CLOSE-1), CLOSE-1)

    # 测试挂单 Cover
    func_test_pending_order(strategy.cover, geno.StopCoverOrder,
                            dict(price_pct=0.01), CLOSE*1.01)
    func_test_pending_order(strategy.cover, geno.LimitCoverOrder,
                            dict(price_pct=-0.01), CLOSE*0.99)
    func_test_pending_order(strategy.cover, geno.StopCoverOrder,
                            dict(price=CLOSE+1), CLOSE+1)
    func_test_pending_order(strategy.cover, geno.LimitCoverOrder,
                            dict(price=CLOSE-1), CLOSE-1)


def test_signals_list():
    go = global_setting()
    go.env.is_save_original = True
    strategy = go.env.strategies['DemoStrategy']
    normal = strategy.buy(100, TICKER)
    pending = strategy.buy(100, TICKER, price=20)
    cancel_pending = strategy.cancel_pending(TICKER, 'long', 10)
    cancel_tst = strategy.cancel_tst(TICKER, 'long', True)
    assert normal in go.env.signals_normal
    assert pending in go.env.signals_pending
    assert cancel_pending in go.env.signals_cancel
    assert cancel_tst in go.env.signals_cancel

    assert normal in go.env.signals_normal_cur
    assert pending in go.env.signals_pending_cur
    assert cancel_pending in go.env.signals_cancel_cur
    assert cancel_tst in go.env.signals_cancel_cur


def test_cancel_pending_order():
    go = global_setting()
    go.env.is_save_original = True
    strategy = go.env.strategies['DemoStrategy']

    def func_cancel_pending(order_func, long_or_short):
        go.env.initialize_env()
        order_func(100, TICKER, price=30)
        order_func(100, TICKER, price=10)
        order_func(100, TICKER, price=2)
        broker = go.env.brokers['StockBroker']
        broker.run()
        assert len(go.env.orders_pending) == 3
        strategy.cancel_pending(TICKER, long_or_short, above_price=20)
        strategy.cancel_pending(TICKER, long_or_short, below_price=3)
        broker.run()
        assert len(go.env.orders_cancel_submitted_cur) == 2
        assert len(go.env.orders_pending) == 1

    func_cancel_pending(strategy.buy, 'long')
    func_cancel_pending(strategy.sell, 'long')
    func_cancel_pending(strategy.short, 'short')
    func_cancel_pending(strategy.cover, 'short')


def test_cancel_tst_order():
    go = global_setting()
    go.env.is_save_original = True
    strategy = go.env.strategies['DemoStrategy']
    broker = go.env.brokers['StockBroker']

    def func_cancel_tst(long_or_short, order_params: dict):
        broker.run()
        assert len(go.env.orders_mkt_submitted_cur) == 1
        mkt_id = go.env.orders_mkt_submitted_cur[0].mkt_id
        assert len(go.env.orders_child_of_mkt_dict[mkt_id]) == 1
        strategy.cancel_tst(TICKER, long_or_short, **order_params)
        broker.run()
        assert len(go.env.orders_child_of_mkt_dict[mkt_id]) == 0

    strategy.buy(100, TICKER, takeprofit=30)
    func_cancel_tst("long", dict(takeprofit=True))
    strategy.buy(100, TICKER, stoploss=30)
    func_cancel_tst("long", dict(stoploss=True))
    strategy.buy(100, TICKER, trailingstop=30)
    func_cancel_tst("long", dict(trailingstop=True))
    strategy.buy(100, TICKER, takeprofit_pct=0.01)
    func_cancel_tst("long", dict(takeprofit=True))
    strategy.buy(100, TICKER, stoploss_pct=0.01)
    func_cancel_tst("long", dict(stoploss=True))
    strategy.buy(100, TICKER, trailingstop_pct=0.01)
    func_cancel_tst("long", dict(trailingstop=True))

    strategy.short(100, TICKER, takeprofit=30)
    func_cancel_tst("short", dict(takeprofit=True))
    strategy.short(100, TICKER, stoploss=30)
    func_cancel_tst("short", dict(stoploss=True))
    strategy.short(100, TICKER, trailingstop=30)
    func_cancel_tst("short", dict(trailingstop=True))
    strategy.short(100, TICKER, takeprofit_pct=0.01)
    func_cancel_tst("short", dict(takeprofit=True))
    strategy.short(100, TICKER, stoploss_pct=0.01)
    func_cancel_tst("short", dict(stoploss=True))
    strategy.short(100, TICKER, trailingstop_pct=0.01)
    func_cancel_tst("short", dict(trailingstop=True))


if __name__ == "__main__":
    test_signals_orders()
    test_cancel_pending_order()
    test_cancel_tst_order()
