from enum import Enum


class ActionType(Enum):

    Buy = 'Buy'
    Sell = 'Sell'
    Short = 'Short'
    Cover = 'Cover'

    Exit_all = 'Exit_all'
    Cancel = 'Cancel'


class OrderType(Enum):

    Market = 'Market'
    Limit = 'Limit'
    Stop = 'Stop'
    Trailing_stop = 'Trailing_stop'

    Limit_pct = 'Limit_pct'
    Stop_pct = 'Stop_pct'
    Trailing_stop_pct = 'Trailing_stop_pct'


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



