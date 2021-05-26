
from event_processing import basic_consumer
from PMD import *
from PMD.EventHandler import EventHandlerResult

class pmd_consumer(basic_consumer):
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)

        # create empty dict if no types passed
        if consumer_args is None:
            consumer_args = {}

        # Process arguments
        parameters = consumer_args.get('parameters', {})
        types = {
            'timestamp_t': 'u8',
            'cluster_id_t': 'u2',
            'cluster_weight_t': 'u4',
            'cluster_color_t': 'u1',
            'xy_t': 'u2'
        }

        self._pmd = PersistentMotionDetector(width, height, parameters, types)

    def process_event_array(self, t, event_buffer, frame_buffer=None):
        del t

        self.init_frame(frame_buffer)

        self._pmd.process_events(event_buffer)
        self._pmd.tick_all(self.event_callback)

    def event_callback(self, e, result: EventHandlerResult, cluster=None):
        x, y, p, t = e
        if result is EventHandlerResult.FILTERED:
            self.draw_event(x, y, p, t, (150, 150, 150))
        elif result is EventHandlerResult.CLUSTERED:
            self.draw_event(x, y, p, t, self._pmd.get_color(cluster))

    def init_frame(self, frame_buffer=None):
        super().init_frame(frame_buffer)

    def draw_event(self, x, y, p, t, color=None):
        if color is None:
            super().draw_event(x, y, p, t)
        else:
            del t, p
            self.frame_to_draw[y, x, :] = color