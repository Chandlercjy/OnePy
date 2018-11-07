
from OnePy.sys_module.components.order_checker import PendingOrderChecker
from OnePy.sys_module.components.order_generator import OrderGenerator
from setting_for_test import TICKER, global_setting


def test_pending_order_checker():
    go = global_setting()
    strategy = go.env.strategies['DemoStrategy']
    go.market_maker.update_market()
    order_generator = OrderGenerator()
    pending_order_checker = PendingOrderChecker()

    go.env.execute_on_close_or_next_open = 'open'

    CLOSE = go.env.feeds[TICKER].current_ohlc['close'] = 11
    HIGH = go.env.feeds[TICKER].current_ohlc['high'] = 20
    LOW = go.env.feeds[TICKER].current_ohlc['low'] = 5
    NEXT_OPEN = go.env.feeds[TICKER].next_ohlc['open'] = 10

    # 挂单带pending
    go.env.initialize_env()
    strategy.buy(100, TICKER, price=12, takeprofit_pct=0.01)

    order_generator.run()  # 提交订单到挂单
    assert len(go.env.orders_pending) == 1

    pending_order_checker.run()  # 触发mkt挂单生成信号
    assert len(go.env.orders_pending) == 0
    assert len(go.env.signals_trigger_cur) == 1
    assert len(go.env.orders_child_of_mkt_dict) == 0

    order_generator.run()  # mkt挂单信号生成为order
    assert len(go.env.orders_mkt_absolute_cur) == 1
    assert len(go.env.signals_trigger_cur) == 0
    assert len(go.env.orders_child_of_mkt_dict) == 1  # 伴随takeprofit挂单

    pending_order_checker.run()  # takeprofit触发生成信号
    assert len(go.env.signals_trigger_cur) == 1

    order_generator.run()  # takeprofit 信号生成为order
    assert len(go.env.orders_mkt_absolute_cur) == 2
    assert len(go.env.signals_trigger_cur) == 0
    assert go.env.orders_mkt_absolute_cur[0].execute_price == 12
    assert go.env.orders_mkt_absolute_cur[1].execute_price == round(
        12*1.01, 3)

    # 市价单带pending
    go.env.initialize_env()
    strategy.buy(100, TICKER, takeprofit_pct=0.01)

    order_generator.run()  # 生成市价单
    assert len(go.env.signals_trigger_cur) == 0
    assert go.env.orders_child_of_mkt_dict != {}
    assert len(go.env.orders_mkt_normal_cur) == 1

    pending_order_checker.run()  # 生成挂单触发信号
    assert go.env.orders_child_of_mkt_dict == {}
    assert len(go.env.signals_trigger_cur) == 1

    order_generator.run()  # 挂单信号成交并转化为order
    assert len(go.env.orders_mkt_absolute_cur) == 1
    assert go.env.orders_mkt_absolute_cur[-1].execute_price == round(
        NEXT_OPEN*1.01, 3)
    assert len(go.env.signals_trigger_cur) == 0
    assert len(go.env.orders_mkt_absolute_cur) == 1
