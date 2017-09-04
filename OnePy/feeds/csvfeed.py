from .feedbase import FeedBase


class ForexCSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''

    dtformat = '%Y%m%d'
    tmformat = '%H:%M:%S'
    timeindex = 'Timestamp'

    def __init__(self, datapath, instrument, fromdate=None,
                 todate=None):
        super(ForexCSVFeed, self).__init__(datapath, instrument,
                                           fromdate, todate)


class TushareCSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''

    dtformat = '%Y-%m-%d'
    tmformat = None
    timeindex = None

    def __init__(self, datapath, instrument, fromdate=None,
                 todate=None):
        super(TushareCSVFeed, self).__init__(datapath, instrument,
                                             fromdate, todate)


class FuturesCSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''

    dtformat = '%Y/%m/%d'
    tmformat = '%H:%M:%S'
    timeindex = 'Time'

    def __init__(self, datapath, instrument, fromdate=None,
                 todate=None):
        super(FuturesCSVFeed, self).__init__(datapath, instrument,
                                             fromdate, todate)


class GenericCSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''
    dtformat = '%Y-%m-%d'
    tmformat = '%H:%M:%S'
    timeindex = None

    def __init__(self, datapath, instrument, fromdate=None, todate=None):
        super(GenericCSVFeed, self).__init__(datapath, instrument, fromdate, todate)