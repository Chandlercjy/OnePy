from OnePy.order.orderbase import Order

# 一定要先注明_ordtype

class BuyOrder(Order):
    _ordtype = "Buy"

class SellOrder(Order):
    _ordtype = "Sell"

class ExitallOrder(Order):
    _ordtype = None

    def __init__(self, marketevent):
        super(ExitallOrder, self).__init__(marketevent)
        self._exectype = "CloseAll"
