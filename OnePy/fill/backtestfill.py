from copy import copy

from OnePy.event import events
from OnePy.fill.fillbase import FillBase


class BacktestFill(FillBase):
    def update_position(self, fillevent):
        f = fillevent
        last_position = self.position[-1]
        if f.exectype in ["Limit", "Stop"]:
            position = last_position
        else:
            position = last_position + f.units * f.direction
        self.position.add(f.date, position)

    def update_margin(self, fillevent):
        """
        计算margin要用到最新position数据，所以在update_position之后
        多头时保证金为正
        空头时保证金为负
        """
        f = fillevent
        margin = self.margin[-1]
        cur_position = self.position[-1]
        if f.exectype in ["Limit", "Stop"]:
            pass
        elif f.target == "Forex":
            margin = f.per_margin * cur_position

        elif f.target == "Futures":
            cur_close = fillevent.price
            margin = f.per_margin * cur_position * f.mult * cur_close

        self.margin.add(f.date, margin)

    def update_avg_price(self, fillevent):
        """计算avg_price要用到最新position数据，所以在update_position之后"""
        f = fillevent
        avg_price = self.avg_price[-1]
        lpod = self.position[-2]
        cpod = self.position[-1]

        if cpod == 0:
            avg_price = 0
        else:
            if f.exectype in ["Stop", "Limit"]:
                pass
            elif lpod == 0:
                avg_price = f.price
            elif lpod > 0:
                if f.ordtype == "Buy":
                    avg_price = (lpod * avg_price + f.units * f.price) / cpod
                elif f.ordtype == "Sell":
                    if cpod > 0:
                        avg_price = (lpod * avg_price - f.units * f.price) / cpod
                    elif cpod < 0:
                        avg_price = f.price

            elif lpod < 0:
                if f.ordtype == "Buy":
                    if cpod > 0:
                        avg_price = f.price
                    elif cpod < 0:
                        avg_price = (-lpod * avg_price - f.units * f.price) / cpod
                elif f.ordtype == "Sell":
                    avg_price = (-lpod * avg_price + f.units * f.price) / cpod
        self.avg_price.add(f.date, abs(avg_price))

    def update_unrealizedPL(self, fillevent):
        """
        用到最新position数据，所以在update_position之后
        运用最新平均价格进行计算, 所以在update_avg_price之后
        """
        f = fillevent
        cur_position = self.position[-1]
        cur_avg = self.avg_price[-1]

        cur_close = f.feed.cur_bar.cur_close  # 当天收盘价
        cur_high = f.feed.cur_bar.cur_high
        cur_low = f.feed.cur_bar.cur_low

        if cur_avg == 0:
            unrealizedPL = unrealizedPL_high = unrealizedPL_low = 0
        else:
            diff = cur_close - cur_avg
            diffh = cur_high - cur_avg
            diffl = cur_low - cur_avg
            unrealizedPL = diff * cur_position * f.mult  # 总利润 = （现价 - 现均价）* 现仓位 * 杠杆
            unrealizedPL_high = diffh * cur_position * f.mult
            unrealizedPL_low = diffl * cur_position * f.mult

        self.unrealizedPL.add(f.date, unrealizedPL,
                              unrealizedPL_high,
                              unrealizedPL_low)

    def update_commission(self, fillevent):
        """更新保证金"""
        f = fillevent
        commission = self.commission[-1]
        per_comm = f.per_comm

        if f.exectype in ["Limit", "Stop"]:
            pass

        elif f.commtype == "FIX":
            if f.target == "Forex":
                per_comm /= f.mult / 10
            elif f.target == "Futures":
                pass
            commission += f.units * per_comm * f.mult

        elif f.commtype == "PCT":
            per_comm *= f.mult  # 交易费为市值的百分比 !!!
            commission += f.units * f.price * per_comm

        self.commission.add(f.date, commission)

    def update_total(self, fillevent):
        """用到最新profit数据，所以在update_profit之后"""
        f = fillevent
        t_re_profit = sum(self.realizedPL.list)
        t_profit = t_re_profit + self.unrealizedPL.total()
        t_profit_high = t_re_profit + self.unrealizedPL.total_high()
        t_profit_low = t_re_profit + self.unrealizedPL.total_low()
        t_commission = self.commission.total()

        balance = self.initial_cash + t_profit - t_commission
        balance_high = self.initial_cash + t_profit_high - t_commission
        balance_low = self.initial_cash + t_profit_low - t_commission

        self.balance.add(f.date, balance, balance_high, balance_low)

    def update_cash(self, fillevent):
        """用到最新total数据，所以在_update_total之后"""
        f = fillevent
        cur_balance = self.balance[-1]

        if f.target in ["Forex", "Futures"]:
            t_margin = self.margin.total()
            cash = cur_balance - t_margin

            self.cash.add(f.date, cash)
        else:
            pass

    def update_info(self, fillevent):
        """更新基本信息"""
        self.update_position(fillevent)

        if fillevent.target in ["Forex", "Futures"]:  # 保证金交易
            self.update_margin(fillevent)
            self.margin.del_last()

        self.update_avg_price(fillevent)
        self.update_unrealizedPL(fillevent)
        self.update_commission(fillevent)
        self.update_total(fillevent)
        self.update_cash(fillevent)

        # 删除重复
        # 第一笔交易会删除update_timeindex产生的初始化信息
        # 第二笔交易开始删除前一笔交易，慢慢迭代，最终剩下最后一笔交易获得的信息
        self.position.del_last()
        self.avg_price.del_last()
        self.unrealizedPL.del_last()
        self.commission.del_last()
        self.cash.del_last()
        self.balance.del_last()

    def update_timeindex(self, feed_list):
        """保持每日开盘后的数据更新"""
        date = feed_list[-1].cur_bar.cur_date

        for feed in feed_list:
            price = feed.cur_bar.cur_close  # 控制计算的价格，同指令成交价一样
            high = feed.cur_bar.cur_high
            low = feed.cur_bar.cur_low

            self.set_dataseries_instrument(feed.instrument)
            self.position.copy_last(date)  # 更新仓位

            # 更新保证金
            if feed.target == "Forex":
                self.margin.copy_last(date)
            elif feed.target == "Futures":
                margin = self.position[-1] * price * feed.per_margin * feed.mult
                self.margin.add(date, margin)

            self.avg_price.copy_last(date)  # 更新平均价格
            self.commission.copy_last(date)  # 更新手续费, 注意期货手续费需要变化，重新计算，这里还没计算

            # 更新利润
            cur_avg = self.avg_price[-1]
            cur_position = self.position[-1]
            unrealizedPL = (price - cur_avg) * cur_position * feed.mult
            unrealizedPL_high = (high - cur_avg) * cur_position * feed.mult
            unrealizedPL_low = (low - cur_avg) * cur_position * feed.mult
            if self.avg_price[-1] == 0:
                unrealizedPL = unrealizedPL_high = unrealizedPL_low = 0

            self.unrealizedPL.add(date, unrealizedPL, unrealizedPL_high, unrealizedPL_low)

        # 更新balance
        commission = self.commission[-1]
        t_re_profit = sum(self.realizedPL.list)
        initial_cash = self.initial_cash
        balance = initial_cash + t_re_profit + self.unrealizedPL.total() - commission  # 初始资金和总利润
        balance_high = initial_cash + t_re_profit + self.unrealizedPL.total_high() - commission
        balance_low = initial_cash + t_re_profit + self.unrealizedPL.total_low() - commission

        self.balance.add(date, balance, balance_high, balance_low)

        # 更新cash
        if feed_list[0].target in ["Forex", "Futures"]:
            t_margin = self.margin.total()
            cash = self.balance[-1] - t_margin
            self.cash.add(date, cash)
        elif feed_list[0].target == "Stock":
            cur_mktv = 0
            for feed in feed_list:
                price = feed.cur_bar.cur_close  # 控制计算的价格，同指令成交价一样
                self.position.set_instrument(feed.instrument)
                cur_mktv += price * self.position[-1]
            cash = self.balance[-1] - cur_mktv
            self.cash.add(date, cash)

        # 检查是否爆仓
        if self.balance[-1] <= 0 or self.cash[-1] <= 0:
            for i in feed_list:
                i.continue_backtest = False
            print("什么破策略啊都爆仓了！！！！")

    def _update_trade_list(self, fillevent):
        """
        根据交易更新trade_list
        若平仓掉了之前的单，如何将单从trade_list中删除，因为没有必要考虑止盈止损了
        情况一：做多，若有空单，将空单逐个抵消，
                        若抵消后有剩余多单，则多开个多单
                        若无，修改原空单
                     若无，直接加多单
        情况二：做空，同情况一相反
        情况三：全部平仓，若有单，将所有空单和多单全部抵消
        情况四：触发止盈止损移动止损，对应单抵消
        """

        f = fillevent
        try:
            last_position = self.position[-2]
        except IndexError:
            last_position = 0

        ls_list = ["TakeProfitOrder", "StopLossOrder", "TralingStopLossOrder"]

        def get_re_profit(trade_units):
            re_profit = (f.price - i.price) * trade_units * f.mult * i.direction
            self.realizedPL.add(f.date, re_profit)

            if self.realizedPL.date[-2] is f.date:
                new_realizedPL = self.realizedPL[-1] + self.realizedPL[-2]
                self.realizedPL.update_cur(new_realizedPL)
                self.realizedPL.del_last()

        if f.exectype in ls_list:  # 检查是否来源于触发了止盈止损的单
            for i in self._trade_list:
                if f.order.parent is i:  # 找到爸爸了
                    self._trade_list.remove(i)  # 删除原空单
                    self._completed_list.append((copy(i), copy(f)))
                    get_re_profit(f.units)
                    f.units = 0
        else:
            if f.ordtype == "Buy" and last_position < 0:  # 若为多单!!!!!!!!!!!!!!!!!!
                for i in self._trade_list:
                    if f.instrument is i.instrument and i.ordtype == "Sell":  # 对应只和空单处理
                        if f.units == 0:
                            break
                        if i.units > f.units:  # 空单大于多单，剩余空单
                            index = self._trade_list.index(i)
                            self._trade_list.pop(index)  # 删除原空单
                            self._completed_list.append((copy(i), copy(f)))

                            i.units = i.units - f.units  # 删除原空单
                            get_re_profit(f.units)
                            f.units = 0

                            if i.units != 0:  # 现事件归零，后面会删除
                                self._trade_list.insert(index, i)  # 将修改完的单子放回原位

                        elif i.units <= f.units:  # 空单小于多单，逐个抵消，即将空单删除
                            self._trade_list.remove(i)  # 删除原空单
                            self._completed_list.append((copy(i), copy(f)))
                            get_re_profit(i.units)
                            f.units = f.units - i.units  # 修改多单仓位，若为0，后面会删除

                        else:
                            print("回测逻辑出错1!!")  # 无作用。用于检查框架逻辑是否有Bug

            elif f.ordtype == "Sell" and last_position > 0:  # 若为空单!!!!!!!!!!!!!!!!!!
                for i in self._trade_list:
                    if f.instrument is i.instrument and i.ordtype == "Buy":  # 对应只和空单处理
                        if f.units == 0:
                            break
                        if i.units > f.units:  # 多单大于空单，剩余多单
                            index = self._trade_list.index(i)
                            self._trade_list.pop(index)  # 删除原空单
                            self._completed_list.append((copy(i), copy(f)))
                            i.units = i.units - f.units  # 修改空单仓位
                            get_re_profit(f.units)
                            f.units = 0
                            if i.units != 0:  # 现事件归零，后面会删除
                                self._trade_list.insert(index, i)  # 将修改完的单子放回原位

                        elif i.units <= f.units:  # 多单小于空单，逐个抵消，即将多单删除
                            self._trade_list.remove(i)  # 删除原多单
                            self._completed_list.append((copy(i), copy(f)))
                            get_re_profit(i.units)
                            f.units = f.units - i.units  # 修改空单仓位，若为0，后面会删除
                        else:
                            print("回测逻辑出错2!!")  # 无作用。用于检查框架逻辑是否有Bug

    def __to_list(self, fillevent):
        """根据情况将order放入list中"""
        if fillevent.exectype in ["Stop", "Limit"]:  # 若是check_trade_list传递过来的，则不append
            self._order_list.append(fillevent)

        else:
            self._update_trade_list(fillevent)
            if fillevent.units != 0:
                self._trade_list.append(fillevent)

    def run_fill(self, fillevent):
        """每次指令发过来后，先直接记录下来，然后再去对冲仓位"""
        self.set_dataseries_instrument(fillevent.instrument)
        self.update_info(fillevent)
        self.__to_list(fillevent)

    def check_trade_list(self, feed):
        """
        存在漏洞，先判断的止盈止损，后判断移动止损
        每次触发止盈止损后，发送一个相反的指令，并且自己对冲掉自己
        因为假设有10个多单，5个止损，5个没止损，若止损时对冲5个没止损的单，则会产生错误
        这种情况只会出现在同时多个Buy或者Sell，且有不同的stop或者limit
        所以给多一个dad属性，用于回去寻找自己以便对冲自己
        """

        def set_take_stop(trade):

            trade.type = "Order"
            if trade.ordtype == "Buy":
                trade.ordtype = "Sell"
            else:
                trade.ordtype = "Buy"
            trade.takeprofit = None
            trade.stoploss = None
            trade.trailingstop = None

            trade.date = data1["date"]
            events.put(trade)

        data1 = feed.cur_bar.cur_data  # 今日的价格
        cur_price = data1[feed.trailingstop_executemode]  # 以这个价格计算移动止损

        # 检查止盈止损,触发交易
        for t in self._trade_list:
            i = copy(t)  # 必须要复制，不然会修改掉原来的订单
            i.order = copy(t.order)
            i.order.set_parent(t)  # 等下要回去原来的列表里面找爸爸

            if i.instrument != feed.instrument:
                continue  # 不是同个instrument无法比较，所以跳过
            if i.takeprofit is i.stoploss is i.trailingstop:
                continue  # 没有止盈止损，所以跳过
            if t.date is data1["date"]:  # 防止当天挂的单，因为昨天的价格而成交，不符合逻辑
                continue

            # 检查移动止损,修改止损价格
            if i.trailingstop:
                i.order.update_trailingstop(cur_price)
                i.trailingstop = i.order.trailingstop

            # 根据指令判断，发送Buy or Sell
            try:
                if i.exectype in ["Stop", "Limit"]:
                    continue

                if i.takeprofit and i.stoploss:
                    if data1["low"] < i.takeprofit < data1["high"] \
                            and data1["low"] < i.stoploss < data1["high"]:
                        print("矛盾的止盈止损，这里选择止损")
                        i.exectype = "StopLossOrder"
                        i.price = i.stoploss
                        set_take_stop(i)
                        continue
                if i.takeprofit:
                    if data1["low"] < i.takeprofit < data1["high"] \
                            or (i.takeprofit < data1["low"] if i.ordtype == "Buy" else False) \
                            or (i.takeprofit > data1["high"] if i.ordtype == "Sell" else False):
                        i.exectype = "TakeProfitOrder"
                        i.price = i.takeprofit
                        set_take_stop(i)
                        continue
                if i.stoploss:
                    if data1["low"] < i.stoploss < data1["high"] \
                            or (i.stoploss > data1["high"] if i.ordtype == "Buy" else False) \
                            or (i.stoploss < data1["low"] if i.ordtype == "Sell" else False):
                        i.exectype = "StopLossOrder"
                        i.price = i.stoploss
                        set_take_stop(i)
                        continue

                if i.trailingstop:
                    if data1["low"] < i.trailingstop < data1["high"] \
                            or (i.trailingstop > data1["high"] if i.ordtype == "Buy" else False) \
                            or (i.trailingstop < data1["low"] if i.ordtype == "Sell" else False):
                        i.exectype = "TralingStopLossOrder"
                        i.price = i.trailingstop
                        set_take_stop(i)
                        continue
            except:
                raise SyntaxError("Catch a Bug!")

    def check_order_list(self, feed):
        """检查挂单是否触发"""
        data1 = feed.cur_bar.cur_data

        def set_event(ordtype, order, change_price=True):
            self._order_list.remove(order)
            if change_price:
                order.price = data1["open"]
            order.type = "Order"

            order.ordtype = ordtype
            order.date = data1["date"]
            order.exectype = f"{order.exectype} Triggered"
            events.put(order)

        for i in self._order_list:
            if i.instrument != feed.instrument:
                continue  # 不是同个instrument无法比较，所以跳过

            # 多单挂单
            if i.ordtype == "Buy":
                if i.exectype == "Stop" and data1["open"] > i.price:
                    set_event("Buy", i)
                elif i.exectype == "Limit" and data1["open"] < i.price:
                    set_event("Buy", i)
                elif data1["low"] < i.price < data1["high"]:
                    set_event("Buy", i, False)  # 按原价成交

            # 空单挂单
            if i.ordtype == "Sell":
                if i.exectype == "Limit" and data1["open"] > i.price:
                    set_event("Sell", i)
                elif i.exectype == "Stop" and data1["open"] < i.price:
                    set_event("Sell", i)
                elif data1["low"] < i.price < data1["high"]:
                    set_event("Sell", i, False)  # 按原价成交
