
import numpy as np
from globals import *

class EventBuffer:
    def __init__(self, width, height, depth):
        self._buffer = np.zeros((width, height, depth), dtype=EVENT_BUFFER_T)
        self._top = np.zeros((width, height), dtype=BUFFER_DEPTH_T)
        self._width = width
        self._height = height

    def count_events(self, t, coordinates):
        x1, y1, x2, y2 = coordinates
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self._width)
        y2 = min(y2, self._height)
        slice = self._buffer[x1:x2, y1:y2, self._top[x1:x2, y1:y2]]
        print(slice)

a = EventBuffer(3, 3, 3)
a._buffer[0,0,0] = 1