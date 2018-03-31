from enum import Enum


class ActionType(Enum):

    Buy = 'buy'
    Sell = 'sell'
    Short = 'short'
    Cover = 'Cover'

    Exit_all = 'exit_all'
    Cancel_all = 'cancel_all'


class OrderType(Enum):

    Market = 'market'
    Limit = 'limit'
    Stop = 'stop'
    Trailing_stop = 'trailing_stop'

    Limit_pct = 'limit_pct'
    Stop_pct = 'stop_pct'
    Trailing_stop_pct = 'trailing_stop_pct'

    Buy = 'buy'
    Sell = 'sell'
    Short_sell = 'short_sell'
    Short_cover = 'short_cover'
    Exit_all = 'exit_all'
    Cancel_all = 'cancel_all'


class ExecTypes(Enum):

    Market_order = "MarketOrder"

    Limit_sell = 'limit_sell'
    Limit_buy = 'limit_buy'
    Stop_buy = 'stop_buy'
    Stop_sell = 'stop_sell'
    Trailing_stop_buy = 'trailing_stop_buy'
    Trailing_stop_sell = 'trailing_stop_sell'

    Limit_short_sell = 'limit_short_sell'
    Stop_short_sell = 'stop_short_sell'
    Limit_cover_short = 'limit_cover_short'
    Stop_cover_short = 'stop_cover_short'
    Trailing_stop_short_sell = 'trailing_stop_short_sell'

    Exit_all = 'exit_all'
    Close_all = "close_all"


class OrderStatus(Enum):

    Created = "Created"
    Submitted = "Submitted"
    Partial = "Partial"
    Completed = "Completed"
    Canceled = "Canceled"
    Expired = "Expired"
    Margin = "Margin"
    Rejected = "Rejected"


class EVENT(Enum):
    Market_updated = 'market_updated'
    Data_cleaned = 'data_cleaned'
    Signal_generated = 'signal_generated'
    Submit_order = 'submit_order'
    Record_result = 'record_result'

    # 系统初始化后触发
    # post_system_init()
    POST_SYSTEM_INIT = 'post_system_init'

    # 在实盘时，你可能需要在此事件后根据其他信息源对系统状态进行调整
    POST_SYSTEM_RESTORED = 'post_system_restored'

    # 策略执行完init函数后触发
    # post_user_init()
    POST_USER_INIT = 'post_user_init'
    # 策略证券池发生变化后触发
    # post_universe_changed(universe)
    POST_UNIVERSE_CHANGED = 'post_universe_changed'

    # 执行before_trading函数前触发
    # pre_before_trading()
    PRE_BEFORE_TRADING = 'pre_before_trading'
    # 该事件会触发策略的before_trading函数
    # before_trading()
    BEFORE_TRADING = 'before_trading'
    # 执行before_trading函数后触发
    # post_before_trading()
    POST_BEFORE_TRADING = 'post_before_trading'

    # 执行handle_bar函数前触发
    # pre_bar()
    PRE_BAR = 'pre_bar'
    # 该事件会触发策略的handle_bar函数
    # bar(bar_dict)
    BAR = 'bar'
    # 执行handle_bar函数后触发
    # post_bar()
    POST_BAR = 'post_bar'

    # 执行handle_tick前触发
    PRE_TICK = 'pre_tick'
    # 该事件会触发策略的handle_tick函数
    # tick(tick)
    TICK = 'tick'
    # 执行handle_tick后触发
    POST_TICK = 'post_tick'

    # 在scheduler执行前触发
    PRE_SCHEDULED = 'pre_scheduled'
    # 在scheduler执行后触发
    POST_SCHEDULED = 'post_scheduled'

    # 执行after_trading函数前触发
    # pre_after_trading()
    PRE_AFTER_TRADING = 'pre_after_trading'
    # 该事件会触发策略的after_trading函数
    # after_trading()
    AFTER_TRADING = 'after_trading'
    # 执行after_trading函数后触发
    # post_after_trading()
    POST_AFTER_TRADING = 'post_after_trading'

    # 结算前触发该事件
    # pre_settlement()
    PRE_SETTLEMENT = 'pre_settlement'
    # 触发结算事件
    # settlement()
    SETTLEMENT = 'settlement'
    # 结算后触发该事件
    # post_settlement()
    POST_SETTLEMENT = 'post_settlement'

    # 创建订单
    # order_pending_new(account, order)
    ORDER_PENDING_NEW = 'order_pending_new'
    # 创建订单成功
    # order_creation_pass(account, order)
    ORDER_CREATION_PASS = 'order_creation_pass'
    # 创建订单失败
    # order_creation_reject(account, order)
    ORDER_CREATION_REJECT = 'order_creation_reject'
    # 创建撤单
    # order_pending_cancel(account, order)
    ORDER_PENDING_CANCEL = 'order_pending_cancel'
    # 撤销订单成功
    # order_cancellation_pass(account, order)
    ORDER_CANCELLATION_PASS = 'order_cancellation_pass'
    # 撤销订单失败
    # order_cancellation_reject(account, order)
    ORDER_CANCELLATION_REJECT = 'order_cancellation_reject'
    # 订单状态更新
    # order_unsolicited_update(account, order)
    ORDER_UNSOLICITED_UPDATE = 'order_unsolicited_update'

    # 成交
    # trade(accout, trade, order)
    TRADE = 'trade'

    ON_LINE_PROFILER_RESULT = 'on_line_profiler_result'

    # persist immediantly
    DO_PERSIST = 'do_persist'

    # 策略被暂停
    STRATEGY_HOLD_SET = 'strategy_hold_set'
    # 策略被恢复
    STRATEGY_HOLD_CANCELLED = 'strategy_hold_canceled'
