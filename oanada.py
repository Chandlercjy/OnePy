import json
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
# import oandapyV20.endpoints.instruments as instruments

from oandapyV20.exceptions import StreamTerminated

from oandapyV20.contrib.requests import (
    MarketOrderRequest,
    TakeProfitDetails,
    StopLossDetails)

# access_token = ''
# accountID = ''



class oanda_api(object):
    def __init__(self):
        self.access_token = access_token
        self.accountID = accountID
        self.client = oandapyV20.API(access_token=access_token)


    def get_accountID(self,access_token):
        return self.accountID

#Order
    def OrderCreate_mkt(self,instrument, units, takeProfit_price, stopLoss_price):
        mktOrder = MarketOrderRequest(instrument=instrument,
                  units=units,
                  takeProfitOnFill=TakeProfitDetails(price=takeProfit_price).data,
                  stopLossOnFill=StopLossDetails(price=stopLoss_price).data
                  ).data
        r = orders.OrderCreate(accountID = self.accountID, data=mktOrder)
        return self.client.request(r)

    def get_OrdersPending(self):
        r = orders.OrdersPending(accountID = self.accountID)
        return self.client.request(r)

    def cancel_all_TAKE_PROFIT_order(self):
        rv = get_OrdersPending()
        idsToCancel = [order.get('id') for order in rv['orders'] if order.get('type') == "TAKE_PROFIT"]
        for orderID in idsToCancel:
            r = orders.OrderCancel(accountID=accountID, orderID=orderID)
            rv = self.client.request(r)

#Trades
    def get_all_oepn_trades(self):
        r = trades.OpenTrades(accountID=accountID)
        return self.client.request(r)

#Positions
    def get_positions(self):
        r = positions.OpenPositions(accountID=accountID)
        return self.client.request(r)


    def get_tickstream(self,instruments_list):
        r = pricing.PricingStream(accountID=accountID, params={"instruments": ",".join(instruments_list)})

        n = 0
        stopAfter = 10 # let's terminate after receiving 3 ticks
        try:
            # the stream requests returns a generator so we can do ...
            for tick in self.client.request(r):
                print json.dumps(tick,indent=2)
                if n >= stopAfter:
                    r.terminate()
                n += 1

        except StreamTerminated as err:
            print("Stream processing ended because we made it stop after {} ticks".format(n))

oanda = oanda_api()
instruments_list = ["EUR_USD"]
# print oanda.get_tickstream(instruments_list)
