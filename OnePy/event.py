
import queue

from OnePy.constants import EVENT


class Event(object):
    """TODO: 添加字典减少内存占用"""

    def __init__(self, event_type, **kwargs):
        self.__dict__ = kwargs
        self.event_type = event_type

    def __repr__(self):
        return ' '.join('{}:{}'.format(k, v) for k, v in self.__dict__.items())


class EventBus(object):
    def __init__(self):
        self.core = queue.Queue()

    def put(self, event):
        self.core.put(event)

    def get(self):
        return self.core.get(block=False)


if __name__ == "__main__":
    a = EVENT
