
from event_processing import basic_consumer

from sys import stdout
import numpy as np

class filter_consumer(basic_consumer):
    '''
    Consumer that incorporates a filter object to only allow some events.
    '''
    def __init__(self, width, height, event_filter, filter_args=None):
        super().__init__(width, height)
        self.filter = event_filter(width, height, **filter_args)

    def process_event_array(self, ts, event_buffer):
        # ignore the timestamp for the default implementation
        del ts
        # fill frame with grey
        self.frame_to_draw = np.full((self.height, self.width, 3), 0.5)
        # draw events colored by polarity
        filtered = 0
        for e in event_buffer:
            if self.filter.is_event_allowed(e):
                filtered += 1
                self.frame_to_draw[e[1], e[0], :] = (e[2], e[2], e[2])

        # display filtering results
        stdout.write('Allowed events: %i/%i(ms) '%(filtered, len(event_buffer)))
        stdout.flush()
    
