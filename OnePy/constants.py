from enum import Enum


class ActionType(Enum):

    Buy = 'Buy'
    Sell = 'Sell'
    Short_sell = 'Short_sell'
    Short_cover = 'Short_cover'

    Exit_all = 'Exit_all'
    Cancel_all = 'Cancel_all'


class OrderType(Enum):

    Market = 'Market'
    Limit = 'Limit'
    Stop = 'Stop'
    Trailing_stop = 'Trailing_stop'

    Limit_pct = 'Limit_pct'
    Stop_pct = 'Stop_pct'
    Trailing_stop_pct = 'Trailing_stop_pct'


class ExecType(Enum):

    Market_order = "MarketOrder"

    Limit_sell = 'Limit_sell'
    Limit_buy = 'Limit_buy'
    Stop_buy = 'Stop_buy'
    Stop_sell = 'Stop_sell'
    Trailing_stop_buy = 'Trailing_stop_buy'
    Trailing_stop_sell = 'Trailing_stop_sell'

    Limit_short_sell = 'Limit_short_sell'
    Stop_short_sell = 'Stop_short_sell'
    Limit_cover_short = 'Limit_cover_short'
    Stop_cover_short = 'Stop_cover_short'
    Trailing_stop_short_sell = 'Trailing_stop_short_sell'

    Exit_all = 'Exit_all'
    Close_all = "Close_all"


class OrderStatus(Enum):

    Created = "Created"
    Submitted = "Submitted"
    Partial = "Partial"
    Completed = "Completed"
    Canceled = "Canceled"
    Expired = "Expired"
    Margin = "Margin"
    Rejected = "Rejected"
    Triggered = "Triggered"


class EVENT(Enum):
    Market_updated = 'Market_updated'
    Data_cleaned = 'Data_cleaned'
    Signal_generated = 'Signal_generated'
    Submit_order = 'Submit_order'
    Record_result = 'Record_result'
