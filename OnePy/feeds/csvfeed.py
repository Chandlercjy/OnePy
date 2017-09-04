from .feedbase import CSVFeedBase


class ForexCSVFeed(CSVFeedBase):
    """
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式，否则为None
    """
    dtformat = "%Y%m%d"
    tmformat = "%H:%M:%S"
    timeindex = "Timestamp"


class TushareCSVFeed(CSVFeedBase):
    """
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式，否则为None
    """

    dtformat = "%Y-%m-%d"
    tmformat = None
    timeindex = None


class FuturesCSVFeed(CSVFeedBase):
    """
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式，否则为None
    """

    dtformat = "%Y/%m/%d"
    tmformat = "%H:%M:%S"
    timeindex = "Time"


class GenericCSVFeed(CSVFeedBase):
    """
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式，否则为None
    """
    dtformat = "%Y-%m-%d"
    tmformat = "%H:%M:%S"
    timeindex = None
