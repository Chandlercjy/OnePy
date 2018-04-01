from OnePy.components.cash_checker import CashChecker
from OnePy.components.market_maker import MarketMaker
from OnePy.components.order_checker import (PendingOrderChecker,
                                            SubmitOrderChecker)
from OnePy.components.order_generator import OrderGenerator
from OnePy.components.signal_generator import SignalGenerator
from OnePy.constants import EVENT
from OnePy.environment import Environment
from OnePy.sys_mod.base_broker import BrokerBase
from OnePy.sys_mod.base_cleaner import CleanerBase
from OnePy.sys_mod.base_reader import DataReaderBase
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_mod.base_riskmanager import RiskManagerBase
from OnePy.sys_mod.base_strategy import StrategyBase
from OnePy.sys_model.bars import Bar
from OnePy.sys_model.orders.base_order import OrderBase
from OnePy.sys_model.record_series import SeriesBase
from OnePy.sys_model.signals import Signal
from OnePy.variables import GlobalVariables

EVENT_LOOP = [dict(if_event=EVENT.Market_updated,
                   then_event=EVENT.Data_cleaned,
                   module_dict=Environment.cleaners),

              dict(if_event=EVENT.Data_cleaned,
                   then_event=EVENT.Signal_generated,
                   module_dict=Environment.strategies),

              dict(if_event=EVENT.Signal_generated,
                   then_event=EVENT.Submit_order,
                   module_dict=Environment.risk_managers),

              dict(if_event=EVENT.Submit_order,
                   then_event=EVENT.Record_result,
                   module_dict=Environment.brokers),

              dict(if_event=EVENT.Record_result,
                   then_event=None,
                   module_dict=Environment.recorders)]

# 在OnePiece中会对sys_modules中的所有模块设置同样的Env和Gvar
SYS_MOD = [
    MarketMaker, SignalGenerator, OrderGenerator,
    SubmitOrderChecker, PendingOrderChecker, CashChecker,
    CleanerBase, StrategyBase, RiskManagerBase, BrokerBase, RecorderBase,
    DataReaderBase, OrderBase
]

SYS_MODEL = [
    Bar, Signal,
    GlobalVariables,
    SeriesBase
]

CUSTOM_MOD = []
