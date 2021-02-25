
from sys import stdout
from event_processing import basic_consumer
from event_processing import basic_filter

class filter_consumer(basic_consumer):
    '''
    Consumer that incorporates a filter object to only allow some events.
    '''
    def __init__(self, width, height, consumer_args):
        super().__init__(width, height)
        event_filter = consumer_args.get('event_filter', basic_filter)
        filter_args = {k.replace('filter_', '',  1): v for (k,v) in consumer_args.items() if k.startswith('filter_')}
        self.filter = event_filter(width, height, **filter_args)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        # ignore the timestamp for the default implementation
        del ts
        # initialize the frame
        self.init_frame(frame_buffer)
        # draw events colored by polarity
        filtered = 0
        for (x, y, p, t) in event_buffer:
            if self.filter.is_event_allowed((x, y, p, t)):
                filtered += 1
                self.draw_event(x, y, p, t)

        # display filtering results
        stdout.write('Processeed %i events'%(len(event_buffer)))
        stdout.flush()
        if filtered>0:
            stdout.write('Allowed %i percent of events'%(filtered/len(event_buffer)*100))
            stdout.flush()
