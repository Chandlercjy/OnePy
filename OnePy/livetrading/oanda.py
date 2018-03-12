import json
import requests
import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.transactions as transactions

import oandapyV20.endpoints.pricing as pricing
# import oandapyV20.endpoints.responses as responses
# import oandapyV20.endpoints.apirequest as apirequest
# import oandapyV20.endpoints.decorators as decorators
import oandapyV20.endpoints.instruments as instruments

from oandapyV20.exceptions import StreamTerminated

from oandapyV20.contrib.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    TakeProfitOrderRequest,
    StopLossOrderRequest,
    TrailingStopLossOrderRequest,
    MITOrderRequest,
    TakeProfitDetails,
    StopLossDetails)

from oandapyV20.definitions.instruments import CandlestickGranularity

from funcy import retry, log_errors
import arrow


class oanda_api(object):
    def __init__(self, accountID, access_token):
        self.access_token = access_token
        self.accountID = accountID
        self.client = oandapyV20.API(access_token=access_token)

    ######################### Account #########################

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_accountID(self, access_token):
        return self.accountID

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_AccountDetails(self):
        r = accounts.AccountDetails(accountID=self.accountID)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_AccountSummary(self):
        r = accounts.AccountSummary(accountID=self.accountID)
        return self.client.request(r)

    ######################### Order #########################
    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_OrderList(self, instrument):
        """
        可以获得特定instrument的 Pending Order
        """
        r = orders.OrderList(accountID=self.accountID,
                             params={"instrument": instrument})
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_OrdersPending(self):
        r = orders.OrdersPending(accountID=self.accountID)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def OrderCreate_mkt(self, instrument, units, takeprofit=None, stoploss=None,
                        trailingstop=None):
        """
        建立市价单
        requesttype:
                MarketOrder
        """
        d = dict(instrument=instrument, units=units)
        if takeprofit:
            d['takeProfitOnFill'] = TakeProfitDetails(price=takeprofit).data
        if stoploss:
            d['stopLossOnFill'] = StopLossDetails(price=stoploss).data
        if trailingstop:
            d['trailingStopLossOnFill'] = TrailingStopLossDetails(price=trailingstop).data

        Order = MarketOrderRequest(**d).data

        r = orders.OrderCreate(accountID=self.accountID, data=Order)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def OrderCreate_pending(self, instrument, units, price, takeprofit=None,
                            stoploss=None, trailingstop=None,
                            requesttype='MarketIfTouchedOrder'):
        """
        建立挂单
        requesttype:
                LimitOrder, StopOrder, MarketIfTouchedOrder,
        """
        d = dict(instrument=instrument, units=units, price=price)
        if takeprofit:
            d['takeProfitOnFill'] = TakeProfitDetails(price=takeprofit).data
        if stoploss:
            d['stopLossOnFill'] = StopLossDetails(price=stoploss).data
        if trailingstop:
            d['trailingStopLossOnFill'] = TrailingStopLossDetails(price=trailingstop).data

        if requesttype is 'MarketIfTouchedOrder':
            Order = MITOrderRequest(**d).data
        elif requesttype is 'LimitOrder':
            Order = LimitOrderRequest(**d).data
        elif requesttype is 'StopOrder':
            Order = StopOrderRequest(**d).data

        r = orders.OrderCreate(accountID=self.accountID, data=Order)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def cancel_all_OrdersPending(self, ordertype, long_short=None):
        """
        撤销全部挂单
        ordertype: LIMIT,STOP，MARKET_IF_TOUCHED，
        buy_sell: LONG, SHORT

        """
        rv = self.get_OrdersPending()
        rv = [dict(id=i.get('id'), units=i.get('units'))
              for i in rv['orders'] if i['type'] in ordertype and i.get('units')]
        if long_short is 'LONG':
            idsToCancel = [order.get('id') for order in rv
                           if float(order['units']) > 0]
        elif long_short is 'SHORT':
            idsToCancel = [order.get('id') for order in rv
                           if float(order['units']) < 0]
        elif long_short is None:
            idsToCancel = [order.get('id') for order in rv]

        for orderID in idsToCancel:
            r = orders.OrderCancel(accountID=self.accountID, orderID=orderID)
            rv = self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def cancel_all_TSTOrder(self, instrument, ordertype):
        """
        撤销全部 止盈， 止损， 追踪止损
        ordertype: TAKE_PROFIT, STOP_LOSS, TRAILING_STOP_LOSS
        """
        rv = self.get_OrderList(instrument)
        idsToCancel = [order.get('id')
                       for order in rv['orders'] if order['type'] in ordertype]
        for orderID in idsToCancel:
            r = orders.OrderCancel(accountID=self.accountID, orderID=orderID)
            rv = self.client.request(r)

            # def OrderCreate_TakeProfit(self,instrument,long_short,price):
            #     """
            #     为所有单添加止盈，但是若止盈已经存在则会报错，此函数暂时不用
            #     long_short: LONG, SHORT
            #     """
            #     rv = self.get_tradeslist(instrument)
            #
            #     if long_short is 'LONG':
            #         idsToCreate = [trade.get('id') for trade in rv['trades']
            #                                  if float(trade['currentUnits']) > 0]
            #     elif long_short is 'SHORT':
            #         idsToCreate = [trade.get('id') for trade in rv['trades']
            #                                  if float(trade['currentUnits']) < 0]
            #     for tradeID in idsToCreate:
            #         Order = TakeProfitOrderRequest(tradeID=tradeID,price=price).data
            #         r = orders.OrderCreate(accountID = self.accountID, data=Order)
            #         rv = self.client.request(r)
            #


        ######################### Trades #########################

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_all_open_trades(self):
        r = trades.OpenTrades(accountID=self.accountID)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_tradeslist(self, instrument):
        r = trades.TradesList(accountID=self.accountID, params={'instrument': instrument})
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_trade_details(self, tradeID):
        r = trades.TradeDetails(accountID=self.accountID, tradeID=tradeID)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def Exitall_trades(self):
        rv = self.get_all_open_trades()
        idsToClose = [trade.get('id') for trade in rv['trades']]
        for tradeID in idsToClose:
            r = trades.TradeClose(accountID=self.accountID, tradeID=tradeID)
            self.client.request(r)


        ######################### Positions #########################

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def close_all_position(self, instrument, closetype='long'):
        """
        closetype: long, short
        """
        if closetype is 'long':
            d = dict(longUnits='ALL')
        elif closetype is 'short':
            d = dict(shortUnits='ALL')
        r = positions.PositionClose(accountID=self.accountID,
                                    instrument=instrument,
                                    data=d)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_positions(self):
        r = positions.OpenPositions(accountID=self.accountID)
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_tickstream(self, instruments_list):
        r = pricing.PricingStream(accountID=self.accountID, params={"instruments": instruments_list})

        n = 0
        stopAfter = 999999999999999999999999999  # let's terminate after receiving 3 ticks
        try:
            # the stream requests returns a generator so we can do ...
            for tick in self.client.request(r):
                print(json.dumps(tick, indent=2))
                if n >= stopAfter:
                    r.terminate()
                n += 1

        except StreamTerminated as err:
            print("Stream processing ended because we made it stop after {} ticks".format(n))


        ######################### Transactions #########################

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_TransactionsSinceID(self, transactionID):
        """TransactionsSinceID.

        Get a range of Transactions for an Account starting at (but not including)
        a provided Transaction ID.
        """
        r = transactions.TransactionsSinceID(accountID=self.accountID,
                                             params={'id': transactionID})
        return self.client.request(r)

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_TransactionDetails(self, transactionID):
        r = transactions.TransactionDetails(accountID=self.accountID,
                                            transactionID=transactionID)
        return self.client.request(r)

    ######################### instrument #########################
    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    # @retry(10,errors=oandapyV20.exceptions.V20Error,timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.SSLError, timeout=lambda a: 2 ** a)
    def get_candlestick_list(self, instrument, granularity, count=50,
                             fromdate=None, todate=None, price='M',
                             smooth=False, includeFirst=None):
        """
        See http://developer.oanda.com/rest-live-v20/instrument-ep/
        instrument: Name of the Instrument [required]
        price: str, 'M' or 'B' or 'A'
        granularity: (S5, S10, S30, M1, M2, M4, M5) <- BAD Interval 
                     M10, M15, M30
                     H1, H2, H3, H4, H6, H8, H12,
                     D, W, M
        count: number of candle, default=50, maximum=5000
        fromdate: format '2017-01-01'
        todate: format '2017-01-01'
        smooth: A smoothed candlestick uses the previous candle’s close
                price as its open price, while an unsmoothed candlestick
                uses the first price from its time range as its open price.
        includeFirst: A flag that controls whether the candlestick that
                      is covered by the from time should be included
                      in the results.
        """
        params = dict(granularity=granularity,
                      count=count,
                      price=price,
                      smooth=smooth,
                      includeFirst=includeFirst)
        if fromdate:
            fromdate += 'T00:00:00Z'
            params.update({'from': fromdate})
        if todate:
            todate += 'T00:00:00Z'
            params.update({'to': todate})
        r = instruments.InstrumentsCandles(instrument=instrument,
                                           params=params)
        return self.client.request(r)

    # 其他

    @retry(10, errors=json.decoder.JSONDecodeError, timeout=lambda a: 2 ** a)
    @retry(10, errors=oandapyV20.exceptions.V20Error, timeout=lambda a: 2 ** a)
    @retry(10, errors=requests.exceptions.ProxyError, timeout=lambda a: 2 ** a)
    def get_pricinginfo(self, instruments_list):
        r = pricing.PricingInfo(accountID=self.accountID,
                                params={"instruments": instruments_list})
        return self.client.request(r)


if __name__ == "__main__":
    from oandakey import access_token, accountID

    oanda = oanda_api(accountID, access_token)
    instrument = "EUR_USD"
    #
    # n=0
    # for i in range(200):
    #     n += 1
    #     print(n)

    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    #     data = oanda.OrderCreate_mkt('EUR_USD',100)
    # data = oanda.OrderCreate_mkt('EUR_USD',10)
    #
    # data = oanda.OrderCreate_mkt('EUR_GBP',-10)
    # data = oanda.OrderCreate_mkt('USD_JPY',10)
    # data = oanda.OrderCreate_pending('EUR_USD',200,1.0,requesttype='LimitOrder')
    # data = oanda.cancel_all_OrdersPending('LIMIT','LONG')
    # data = oanda.cancel_all_OrdersPending('LIMIT','SHORT')
    # data = oanda.cancel_all_OrdersPending('STOP','SHORT')
    # data = oanda.cancel_all_OrdersPending('STOP','LONG')
    # data = oanda.cancel_all_TSTOrder('EUR_USD','TAKE_PROFIT')
    # data = oanda.Exitall_trades()
    # data = oanda.get_OrdersPending()
    # oandƒa.get_tickstream([instrument])
    data = oanda.get_candlestick_list(instrument, 'S30',count=5000,fromdate="2017-01-01")
    # data = oanda.get_tradeslist(instrument)
    # data = oanda.get_AccountDetails()
    # print(data)
    # data = oanda.get_AccountSummary()
    # data = oanda.close_all_position('EUR_USD','long')
    # data= oanda.get_TransactionsSinceID(1)
    # data = oanda.get_positions()
    print(json.dumps(data, indent=2))
    # print(len(data['positions'][0]['long']['tradeIDs'])) # 获得订单数


    #Check interval test
    from datetime import timedelta
    def check_candles_interval(data,interval):
        bar_list = []
        for i in range(len(data['candles'])):
            gg = arrow.get(data['candles'][i+1]['time'])-arrow.get(data['candles'][i]['time'])
            if gg != timedelta(interval/60/60/24) and gg != timedelta(interval/60/60/24 +2) :
                print(gg)
                print(data['candles'][i+1]['time'])
                print(arrow.get(data['candles'][i]['time']))
    # check_candles_interval(data,30)