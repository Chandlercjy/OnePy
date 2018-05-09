import OnePy as op
from OnePy.builtin_module.data_readers.csvreader import CSVReader
from OnePy.builtin_module.recorders.stock_recorder import StockRecorder
from OnePy.constants import ActionType
from OnePy.sys_module.base_broker import StockBroker
from OnePy.sys_module.components.cash_checker import CashChecker
from OnePy.sys_module.components.order_checker import (PendingOrderChecker,
                                                       SubmitOrderChecker)
from OnePy.sys_module.components.order_generator import OrderGenerator
from OnePy.sys_module.models.orders import general_order as geno

TICKER = '000001'
START = '2018-01-03'
END = '2018-01-06'


class DemoStrategy(op.StrategyBase):
    pass


def global_setting():
    global go, strategy, order_generator
    CSVReader('./000001.csv', ticker=TICKER, fromdate=START, todate=END)
    strategy = DemoStrategy()
    StockBroker()
    StockRecorder().set_setting(initial_cash=100000,
                                comm=1, comm_pct=None, margin_rate=0.1)
    go = op.OnePiece()
    go._initialize_trading_system()
    go.market_maker.update_market()
    order_generator = OrderGenerator()


def test_signals_orders():
    global_setting()
    go.env.execute_on_close_or_next_open = 'open'

    CLOSE = go.env.feeds[TICKER].current_ohlc['close'] = 11
    HIGH = go.env.feeds[TICKER].current_ohlc['high'] = 20
    LOW = go.env.feeds[TICKER].current_ohlc['low'] = 5
    NEXT_OPEN = go.env.feeds[TICKER].next_ohlc['open'] = 10

    # 测试 Buy 指令
    signal = strategy.buy(
        100, TICKER, takeprofit=10, stoploss=10, trailingstop=10)

    assert signal in go.env.signals_normal
    assert signal in go.env.signals_normal_cur
    assert signal.action_type == ActionType.Buy

    order_generator.run()
    mkt_order = go.env.orders_mkt_normal[0]
    assert mkt_order.signal is signal
    assert mkt_order.is_pure() is False
    assert mkt_order.first_cur_price == mkt_order.execute_price == NEXT_OPEN
    assert mkt_order.father_mkt_id is None
    pending_orders = go.env.orders_pending_mkt_dict[mkt_order.mkt_id]

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

    assert stop_sell.trigger_key == 'stoploss'
    assert limit_sell.trigger_key == 'takeprofit'
    assert trailingstop_sell.trigger_key == 'trailingstop'
    assert stop_sell.signal == limit_sell.signal == trailingstop_sell.signal
    assert stop_sell.mkt_id == limit_sell.mkt_id == trailingstop_sell.mkt_id
    assert stop_sell.target_price == NEXT_OPEN - 10/100
    assert limit_sell.target_price == NEXT_OPEN + 10/100
    assert trailingstop_sell.initialize_latest_target_price() == NEXT_OPEN - 10/100
    assert NEXT_OPEN-10/100 <= trailingstop_sell.target_price <= HIGH - 10/100

    # 测试 Buy 指令,带pct
    go.env.refresh()
    signal = strategy.buy(
        100, TICKER, takeprofit_pct=0.1, stoploss_pct=0.1, trailingstop_pct=0.1)

    assert signal in go.env.signals_normal
    assert signal in go.env.signals_normal_cur
    assert signal.action_type == ActionType.Buy

    order_generator.run()
    mkt_order = go.env.orders_mkt_normal[0]
    assert mkt_order.signal is signal
    assert mkt_order.is_pure() is False
    assert mkt_order.first_cur_price == mkt_order.execute_price == NEXT_OPEN
    assert mkt_order.father_mkt_id is None
    pending_orders = go.env.orders_pending_mkt_dict[mkt_order.mkt_id]

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

    assert stop_sell.trigger_key == 'stoploss_pct'
    assert limit_sell.trigger_key == 'takeprofit_pct'
    assert trailingstop_sell.trigger_key == 'trailingstop_pct'
    assert stop_sell.signal == limit_sell.signal == trailingstop_sell.signal
    assert stop_sell.mkt_id == limit_sell.mkt_id == trailingstop_sell.mkt_id
    assert stop_sell.target_price == round(NEXT_OPEN*0.9, 3)
    assert limit_sell.target_price == round(NEXT_OPEN*1.1, 3)
    assert trailingstop_sell.initialize_latest_target_price() == round(NEXT_OPEN*0.9, 3)
    assert NEXT_OPEN*0.9 <= trailingstop_sell.target_price <= HIGH - NEXT_OPEN*0.1

    go.env.refresh()
    # 测试挂单 Buy
    signal = strategy.buy(100, TICKER, price_pct=0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopBuyOrder) is True
    assert pending_order.target_price == round(CLOSE*1.01, 3)

    go.env.refresh()
    signal = strategy.buy(100, TICKER, price_pct=-0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitBuyOrder) is True
    assert pending_order.target_price == round(CLOSE*0.99, 3)

    go.env.refresh()
    signal = strategy.buy(100, TICKER, price=CLOSE)
    order_generator.run()
    assert len(go.env.orders_mkt_absolute) == 1

    go.env.refresh()
    signal = strategy.buy(100, TICKER, price=CLOSE + 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopBuyOrder) is True
    assert pending_order.target_price == CLOSE+1

    go.env.refresh()
    signal = strategy.buy(100, TICKER, price=CLOSE - 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitBuyOrder) is True
    assert pending_order.target_price == CLOSE-1

    # 测试Sell
    go.env.refresh()
    signal = strategy.sell(100, TICKER)
    order_generator.run()
    mkt_order = go.env.orders_mkt_normal[0]
    assert mkt_order.execute_price == NEXT_OPEN

    # 测试挂单Sell
    go.env.refresh()
    signal = strategy.sell(100, TICKER, price_pct=0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitSellOrder) is True
    assert pending_order.target_price == round(CLOSE*1.01, 3)

    go.env.refresh()
    signal = strategy.sell(100, TICKER, price_pct=-0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopSellOrder) is True
    assert pending_order.target_price == round(CLOSE*0.99, 3)

    go.env.refresh()
    signal = strategy.sell(100, TICKER, price=CLOSE + 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitSellOrder) is True
    assert pending_order.target_price == CLOSE+1

    go.env.refresh()
    signal = strategy.sell(100, TICKER, price=CLOSE - 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopSellOrder) is True
    assert pending_order.target_price == CLOSE-1

    # 测试 Short Sell
    go.env.refresh()
    signal = strategy.short_sell(
        100, TICKER, takeprofit=10, stoploss=10, trailingstop=10)

    assert signal in go.env.signals_normal
    assert signal in go.env.signals_normal_cur
    assert signal.action_type == ActionType.Short_sell

    order_generator.run()
    mkt_order = go.env.orders_mkt_normal[0]
    assert mkt_order.signal is signal
    assert mkt_order.is_pure() is False
    assert mkt_order.first_cur_price == mkt_order.execute_price == NEXT_OPEN
    assert mkt_order.father_mkt_id is None  # TODO
    pending_orders = go.env.orders_pending_mkt_dict[mkt_order.mkt_id]

    for order in pending_orders:
        assert order.action_type == ActionType.Short_cover

        if isinstance(order, geno.StopCoverShortOrder):
            stop_cover_short = order
        elif isinstance(order, geno.LimitCoverShortOrder):
            limit_cover_short = order
        elif isinstance(order, geno.TrailingStopCoverShortOrder):
            trailingstop_cover_short = order
        else:
            raise Exception("This can't be raised")

    assert stop_cover_short.trigger_key == 'stoploss'
    assert limit_cover_short.trigger_key == 'takeprofit'
    assert trailingstop_cover_short.trigger_key == 'trailingstop'
    assert stop_cover_short.signal == limit_cover_short.signal == trailingstop_cover_short.signal
    assert stop_cover_short.mkt_id == limit_cover_short.mkt_id == trailingstop_cover_short.mkt_id
    assert stop_cover_short.target_price == NEXT_OPEN + 10/100
    assert limit_cover_short.target_price == NEXT_OPEN - 10/100
    assert trailingstop_cover_short.initialize_latest_target_price() == NEXT_OPEN + \
        10/100
    assert LOW + 10/100 <= trailingstop_cover_short.target_price <= NEXT_OPEN + 10/100

    # 测试 Short Sell 指令,带pct
    go.env.refresh()
    signal = strategy.short_sell(
        100, TICKER, takeprofit_pct=0.1, stoploss_pct=0.1, trailingstop_pct=0.1)

    assert signal in go.env.signals_normal
    assert signal in go.env.signals_normal_cur
    assert signal.action_type == ActionType.Short_sell

    order_generator.run()
    mkt_order = go.env.orders_mkt_normal[0]
    assert mkt_order.signal is signal
    assert mkt_order.is_pure() is False
    assert mkt_order.first_cur_price == mkt_order.execute_price == NEXT_OPEN
    assert mkt_order.father_mkt_id is None  # TODO
    pending_orders = go.env.orders_pending_mkt_dict[mkt_order.mkt_id]

    for order in pending_orders:
        assert order.action_type == ActionType.Short_cover

        if isinstance(order, geno.StopCoverShortOrder):
            stop_cover_short = order
        elif isinstance(order, geno.LimitCoverShortOrder):
            limit_cover_short = order
        elif isinstance(order, geno.TrailingStopCoverShortOrder):
            trailingstop_cover_short = order
        else:
            raise Exception("This can't be raised")

    assert stop_cover_short.trigger_key == 'stoploss_pct'
    assert limit_cover_short.trigger_key == 'takeprofit_pct'
    assert trailingstop_cover_short.trigger_key == 'trailingstop_pct'
    assert stop_cover_short.signal == limit_cover_short.signal == trailingstop_cover_short.signal
    assert stop_cover_short.mkt_id == limit_cover_short.mkt_id == trailingstop_cover_short.mkt_id
    assert stop_cover_short.target_price == round(NEXT_OPEN*1.1, 3)
    assert limit_cover_short.target_price == round(NEXT_OPEN*0.9, 3)
    assert trailingstop_cover_short.initialize_latest_target_price() == round(NEXT_OPEN*1.1, 3)
    assert LOW+NEXT_OPEN*0.1 <= trailingstop_cover_short.target_price <= NEXT_OPEN*1.1

    # 测试挂单 Short Sell
    go.env.refresh()
    signal = strategy.short_sell(100, TICKER, price_pct=0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitShortSellOrder) is True
    assert pending_order.target_price == round(CLOSE*1.01, 3)

    go.env.refresh()
    signal = strategy.short_sell(100, TICKER, price_pct=-0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopShortSellOrder) is True
    assert pending_order.target_price == round(CLOSE*0.99, 3)

    go.env.refresh()
    signal = strategy.short_sell(100, TICKER, price=CLOSE)
    order_generator.run()
    assert len(go.env.orders_mkt_absolute) == 1

    go.env.refresh()
    signal = strategy.short_sell(100, TICKER, price=CLOSE + 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitShortSellOrder) is True
    assert pending_order.target_price == CLOSE+1

    go.env.refresh()
    signal = strategy.short_sell(100, TICKER, price=CLOSE - 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopShortSellOrder) is True
    assert pending_order.target_price == CLOSE-1

    # 测试Short Cover
    go.env.refresh()
    signal = strategy.short_cover(100, TICKER)
    order_generator.run()
    mkt_order = go.env.orders_mkt_normal[0]
    assert mkt_order.execute_price == NEXT_OPEN

    # 测试挂单Short Cover
    go.env.refresh()
    signal = strategy.short_cover(100, TICKER, price_pct=0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopCoverShortOrder) is True
    assert pending_order.target_price == round(CLOSE*1.01, 3)

    go.env.refresh()
    signal = strategy.short_cover(100, TICKER, price_pct=-0.01)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitCoverShortOrder) is True
    assert pending_order.target_price == round(CLOSE*0.99, 3)

    go.env.refresh()
    signal = strategy.short_cover(100, TICKER, price=CLOSE + 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.StopCoverShortOrder) is True
    assert pending_order.target_price == CLOSE+1

    go.env.refresh()
    signal = strategy.short_cover(100, TICKER, price=CLOSE - 1)
    order_generator.run()
    pending_order = go.env.orders_pending[0]
    assert isinstance(pending_order, geno.LimitCoverShortOrder) is True
    assert pending_order.target_price == CLOSE-1


def test_submit_order_checker():
    global_setting()
    order_checker = SubmitOrderChecker(CashChecker.stock_checker)

    go.env.execute_on_close_or_next_open = 'open'
    NEXT_OPEN = go.env.feeds[TICKER].next_ohlc['open'] = 10

    # 测试 缺少position
    strategy.sell(100, TICKER)
    strategy.short_cover(100, TICKER)
    order_generator.run()
    order_checker.run()
    assert go.env.orders_mkt_submitted == []

    # 测试 缺少cash
    go.env.refresh()
    strategy.buy(100, TICKER)
    strategy.buy(100, TICKER)
    go.env.recorder.cash[-1]['value'] = NEXT_OPEN*100
    order_generator.run()
    order_checker.run()
    assert len(go.env.orders_mkt_submitted) == 1

    go.env.refresh()
    strategy.buy(100, TICKER)
    strategy.buy(100, TICKER)
    go.env.recorder.cash[-1]['value'] = NEXT_OPEN*100 - 1
    order_generator.run()
    order_checker.run()
    assert go.env.orders_mkt_submitted == []

    go.env.refresh()
    strategy.buy(100, TICKER)
    strategy.buy(100, TICKER)
    go.env.recorder.cash[-1]['value'] = NEXT_OPEN*100 + 1
    order_generator.run()
    order_checker.run()
    assert len(go.env.orders_mkt_submitted) == 1

    # 测试 partial 成交
    go.env.refresh()
    strategy.sell(100, TICKER)
    strategy.short_cover(100, TICKER)
    long_po = go.env.recorder.position.data['000001_long'][-1]['value'] = 30
    short_po = go.env.recorder.position.data['000001_short'][-1]['value'] = 40
    order_generator.run()
    order_checker.run()
    assert len(go.env.orders_mkt_submitted) == 2

    for order in go.env.orders_mkt_submitted:
        if order.action_type == ActionType.Sell:
            assert order.size == long_po
        elif order.action_type == ActionType.Short_cover:
            assert order.size == short_po
        else:
            raise Exception("This can't be raised")


def test_pending_order_checker():
    global_setting()
    pending_order_checker = PendingOrderChecker()

    go.env.execute_on_close_or_next_open = 'open'

    CLOSE = go.env.feeds[TICKER].current_ohlc['close'] = 11
    HIGH = go.env.feeds[TICKER].current_ohlc['high'] = 20
    LOW = go.env.feeds[TICKER].current_ohlc['low'] = 5
    NEXT_OPEN = go.env.feeds[TICKER].next_ohlc['open'] = 10

    # 纯挂单
    strategy.buy(100, TICKER, price=11)
    order_generator.run()
    pending_order_checker.run()
    assert len(go.env.orders_mkt_absolute) == 1

    # 挂单带pending
    go.env.refresh()
    strategy.buy(100, TICKER, price=12, takeprofit_pct=0.01)

    order_generator.run()  # 提交订单到挂单
    assert len(go.env.orders_pending) == 1

    pending_order_checker.run()  # 触发mkt挂单生成信号
    assert len(go.env.orders_pending) == 0
    assert len(go.env.signals_trigger_cur) == 1
    assert len(go.env.orders_pending_mkt_dict) == 0

    order_generator.run()  # mkt挂单信号生成为order
    assert len(go.env.orders_mkt_absolute) == 1
    assert len(go.env.signals_trigger_cur) == 0
    assert len(go.env.orders_pending_mkt_dict) == 1  # 伴随takeprofit挂单

    pending_order_checker.run()  # takeprofit触发生成信号
    assert len(go.env.signals_trigger_cur) == 1

    order_generator.run()  # takeprofit 信号生成为order
    assert len(go.env.orders_mkt_absolute) == 2
    assert len(go.env.signals_trigger_cur) == 0
    assert go.env.orders_mkt_absolute[0].execute_price == 12
    assert go.env.orders_mkt_absolute[1].execute_price == round(
        12*1.01, 3)

    # 市价单带pending
    go.env.refresh()
    strategy.buy(100, TICKER, takeprofit_pct=0.01)

    order_generator.run()  # 生成市价单
    assert len(go.env.signals_trigger_cur) == 0
    assert go.env.orders_pending_mkt_dict != {}
    assert len(go.env.orders_mkt_normal) == 1

    pending_order_checker.run()  # 生成挂单触发信号
    assert go.env.orders_pending_mkt_dict == {}
    assert len(go.env.signals_trigger_cur) == 1

    order_generator.run()  # 挂单信号成交并转化为order
    assert len(go.env.orders_mkt_absolute) == 1
    assert go.env.orders_mkt_absolute[-1].execute_price == round(
        NEXT_OPEN*1.01, 3)
    assert len(go.env.signals_trigger_cur) == 0
    assert len(go.env.orders_mkt_absolute) == 1
