from OnePy.builtin_module.plotters.by_plotly import PlotBase
from OnePy.builtin_module.trade_log.match_engine import MatchEngine
from OnePy.constants import EVENT
from OnePy.environment import Environment

# 控制事件发生顺序
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
