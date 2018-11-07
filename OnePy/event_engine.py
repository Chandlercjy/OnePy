
import queue

from OnePy.constants import EVENT


class EventEngine(object):
    def __init__(self):
        self._core = queue.Queue()  # type:queue.Queue

    def put(self, event: EVENT):
        self._core.put(event)

    def get(self) -> EVENT:
        return self._core.get(block=False)

    def is_empty(self) -> bool:
        return self._core.empty()
