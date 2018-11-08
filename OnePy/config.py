from OnePy.builtin_module.backtest_forex.forex_bar import BarForex
from OnePy.builtin_module.backtest_stock.stock_bar import BarAshares
from OnePy.constants import EVENT
from OnePy.sys_module.metabase_env import OnePyEnvBase

# 控制事件发生顺序
EVENT_LOOP = [dict(if_event=EVENT.Market_updated,
                   then_event=EVENT.Data_cleaned,
                   module_dict=OnePyEnvBase.env.cleaners),

              dict(if_event=EVENT.Data_cleaned,
                   then_event=EVENT.Signal_generated,
                   module_dict=OnePyEnvBase.env.strategies),

              dict(if_event=EVENT.Signal_generated,
                   then_event=EVENT.Submit_order,
                   module_dict=OnePyEnvBase.env.risk_managers),

              dict(if_event=EVENT.Submit_order,
                   then_event=EVENT.Record_result,
                   module_dict=OnePyEnvBase.env.brokers),

              dict(if_event=EVENT.Record_result,
                   then_event=None,
                   module_dict=OnePyEnvBase.env.recorders)]
