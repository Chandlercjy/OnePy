from OnePy.sys_module.base_riskmanager import RiskManagerBase


class StockLimitFilterRiskManager(RiskManagerBase):
    """过滤第二天涨停牌的信号"""

    def filter_signal(self):
        """目前只考虑open成交"""
        feeds = self.env.feeds

        for signal in self.env.signals_normal_cur[:]:
            bar = feeds[signal.ticker]
            is_above_limit_up = bar.execute_price >= bar.close*1.1
            is_below_limit_down = bar.execute_price <= bar.close*0.9

            if is_above_limit_up or is_below_limit_down:
                self.env.signals_normal_cur.remove(signal)

        for signal in self.env.signals_trigger_cur[:]:
            bar = feeds[signal.ticker]
            is_above_limit_up = signal.execute_price >= bar.close*1.1
            is_below_limit_down = signal.execute_price <= bar.close*0.9

            if is_above_limit_up or is_below_limit_down:
                self.env.signals_trigger_cur.remove(signal)



    def run(self):
        self.filter_signal()
