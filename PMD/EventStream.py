
import numpy as np

class EventStream:
    def __init__(self, width, height, x_div, y_div, types=None):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._xy_t = types.get('xy_t', 'u2')

        # Initialize
        self._width = width
        self._height = height
        self._x_boundaries = np.array([(width/x_div)*i for i in range(1, x_div)], dtype=self._xy_t)
        self._y_boundaries = np.array([(height/y_div)*i for i in range(1, y_div)], dtype=self._xy_t)
    
    def place_events(self, event_buffer, filetype):
        if filetype == '.aedat4':
            return np.transpose(self.place_event(event_buffer[:,0], event_buffer[:,1]))
        else:
            return np.transpose(self.place_event(event_buffer[:]['x'], event_buffer[:]['y']))

    def place_event(self, x, y):
        dest = (
            np.searchsorted(self._x_boundaries, x),
            np.searchsorted(self._y_boundaries, y)
        )
        return dest
