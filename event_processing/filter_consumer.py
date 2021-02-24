
from event_processing import basic_consumer

from sys import stdout

class filter_consumer(basic_consumer):
    '''
    Consumer that incorporates a filter object to only allow some events.
    '''
    def __init__(self, width, height, event_filter, filter_args=None):
        super().__init__(width, height)
        self.filter = event_filter(width, height, **filter_args)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        # ignore the timestamp for the default implementation
        del ts
        # initialize the frame
        self.init_frame(frame_buffer)
        # draw events colored by polarity
        filtered = 0
        for e in event_buffer:
            if self.filter.is_event_allowed(e):
                filtered += 1
                self.draw_event(e)

        # display filtering results
        if filtered>0:
            stdout.write('Allowed %i percent of events'%(filtered/len(event_buffer)*100))
            stdout.flush()
