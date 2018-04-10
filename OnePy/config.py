from OnePy.builtin_module.plotters.by_plotly import PlotBase
from OnePy.constants import EVENT
from OnePy.environment import Environment
from OnePy.sys_module.base_broker import BrokerBase
from OnePy.sys_module.base_cleaner import CleanerBase
from OnePy.sys_module.base_reader import DataReaderBase
from OnePy.sys_module.base_recorder import RecorderBase
from OnePy.sys_module.base_riskmanager import RiskManagerBase
from OnePy.sys_module.base_strategy import StrategyBase
from OnePy.sys_module.components.cash_checker import CashChecker
from OnePy.sys_module.components.market_maker import MarketMaker
from OnePy.sys_module.components.match_engine import MatchEngine
from OnePy.sys_module.components.order_checker import (PendingOrderChecker,
                                                       SubmitOrderChecker)
from OnePy.sys_module.components.order_generator import OrderGenerator
from OnePy.sys_module.components.output import OutPut
from OnePy.sys_module.components.signal_filter import SignalFilter
from OnePy.sys_module.components.signal_generator import SignalGenerator
from OnePy.sys_module.models.bars import Bar
from OnePy.sys_module.models.base_series import CashSeries, SeriesBase
from OnePy.sys_module.models.orders.base_order import OrderBase
from OnePy.sys_module.models.signals import Signal
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

# 在OnePiece中会对sys_modules中的所有模块设置同样的Env
SYS_MODULE = [
    MarketMaker, SignalGenerator, OrderGenerator,
    SubmitOrderChecker, PendingOrderChecker, CashChecker, SignalFilter,
    MatchEngine, OutPut,
    CleanerBase, StrategyBase, RiskManagerBase, BrokerBase, RecorderBase,
    DataReaderBase, OrderBase
]

SYS_MODEL = [
    Bar, Signal,
    GlobalVariables, PlotBase,
    SeriesBase, CashSeries, PlotBase
]

CUSTOM_MODULE = []
