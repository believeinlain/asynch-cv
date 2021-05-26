
from collections import deque

class InputQueue:
    def __init__(self, depth=32):
        self._queue = deque(maxlen = depth)

    def push(self, event):
        self._queue.append(event)
    
    def push_multiple(self, events):
        self._queue.extend(events)

    def pop(self):
        return self._queue.popleft() if len(self._queue) > 0 else None