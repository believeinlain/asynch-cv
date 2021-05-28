
import cv2
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
        # explicitly set types to ensure consistency between modules
        types = {
            'timestamp_t': 'u8',
            'cluster_id_t': 'u2',
            'cluster_weight_t': 'u4',
            'cluster_color_t': 'u1',
            'xy_t': 'u2',
            'xy_sum_t': 'u4'
        }

        self._pmd = PersistentMotionDetector(width, height, parameters, types)

    def process_event_array(self, t, event_buffer, frame_buffer=None):

        self.init_frame(frame_buffer)

        self._pmd.process_events(event_buffer)
        self._pmd.tick_all(t, self.event_callback, self.cluster_callback)

    def event_callback(self, e, result: EventHandlerResult, cluster=None):
        x, y, p, t = e
        if result is EventHandlerResult.FILTERED:
            self.draw_event(x, y, p, t, (150, 150, 150))
        elif result is EventHandlerResult.CLUSTERED:
            self.draw_event(x, y, p, t, self._pmd.get_color(cluster))

    def cluster_callback(self, id, centroid, weight, bb=None):
        int_c = tuple(np.array(centroid, dtype=np.uint16))
        color = tuple(self._pmd.get_color(id).tolist())

        # draw the region centroid
        cv2.circle(self.frame_to_draw, int_c, 1, color, thickness=2)

        # draw weight
        cv2.putText(self.frame_to_draw, f'{weight}', int_c, cv2.FONT_HERSHEY_PLAIN,
            1, tuple(color), 1, cv2.LINE_AA)

        # draw bb if given
        if bb is not None:
            x, y, w, h = bb
            cv2.rectangle(self.frame_to_draw, (x, y), (x+w, y+h), color, 1)
                    

    def init_frame(self, frame_buffer=None):
        super().init_frame(frame_buffer)

        colors, assigned = self._pmd.get_cluster_map()
        
        self.frame_to_draw[assigned] = np.multiply(0.5, colors)

    def draw_event(self, x, y, p, t, color=None):
        if color is None:
            super().draw_event(x, y, p, t)
        else:
            del t, p
            self.frame_to_draw[y, x, :] = color