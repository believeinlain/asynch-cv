
from collections import deque

class InputQueue:
    def __init__(self, depth):
        self._queue = deque(maxlen = depth)

    def push(self, event):
        self._queue.append(event)

    def pop(self):
        return self._queue.popleft()