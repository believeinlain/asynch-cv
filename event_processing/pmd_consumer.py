# pyright: reportMissingImports=false

import cv2
import numpy as np
from colorsys import hsv_to_rgb
from event_processing import basic_consumer
from PMD import PyPMD

class pmd_consumer(basic_consumer):
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)

        # Process arguments
        self._filetype = self._consumer_args.get('filetype', '.raw')
        parameters = self._consumer_args.get('parameters', {})
        # explicitly set types to ensure consistency between modules
        types = {}

        # get needed types to set colors
        self._cluster_color_t = types.get('cluster_color_t', 'u1')
        self._cluster_id_t = types.get('cluster_id_t', 'u2')
        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._max_clusters = self._unassigned + 1
        # pick a different color for each region
        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._max_clusters = self._unassigned + 1
        self._cluster_color = np.zeros((self._max_clusters, 3), dtype=self._cluster_color_t)
        for i in range(self._max_clusters):
            self._cluster_color[i] = np.multiply(255.0, 
                hsv_to_rgb((i*np.pi % 3.6)/3.6, 1.0, 1.0), casting='unsafe')

        self._pmd = PyPMD.PyPMD(width, height, parameters)

        # self._metrics = DetectionMetrics(['boat', 'RHIB'])
        # self._detections = []
    
    def process_event_buffer(self, ts, event_buffer):
        # we don't care about ts
        del ts
        # pass events to the pmd to draw
        self.frame_to_draw = self._pmd.process_events(self.frame_to_draw, event_buffer)

    # def event_callback(self, e, result, cluster=None):
    #     x, y, p, t = e
    #     if result == 1:
    #         self.draw_event(x, y, p, t, (150, 150, 150))
    #     elif result == 2:
    #         self.draw_event(x, y, p, t, self._cluster_color[cluster])

    # def cluster_callback(self, id, results):
    #     centroid = tuple(results['centroid'])
    #     color = tuple(self._cluster_color[id].tolist())

    #     # draw stats if detected
    #     if results['is_detected']:
    #         # find the bounding box
    #         image = np.transpose(self._pmd.get_single_cluster_map(id))
    #         x, y, w, h = cv2.boundingRect(image)
    #         cv2.rectangle(self.frame_to_draw, (x, y), (x+w, y+h), color, 1)
    #         cv2.circle(self.frame_to_draw, centroid, 30, color, thickness=1)

    #         # save the detection
    #         results['bb'] = (x, y, x+w, y+h)
    #         self._detections[self.frame_count].append(results)

    #     # draw confidence
    #     cv2.putText(self.frame_to_draw, f"{results['confidence']:0.2f}", centroid, cv2.FONT_HERSHEY_PLAIN,
    #         1, tuple(color), 1, cv2.LINE_AA)
        
    #     # draw arrow if endpoint given
    #     if results['endpoint'] is not None:
    #         cv2.arrowedLine(self.frame_to_draw, centroid, tuple(results['endpoint']), color, thickness=1)

    def init_frame(self, frame_buffer=None):
        super().init_frame(frame_buffer)

        # ids, assigned = self._pmd.get_cluster_map()
        
        # self.frame_to_draw[assigned] = np.multiply(0.5, self._cluster_color[ids])

        # add an empty list for this frame's detections
        # self._detections.append([])

    def draw_frame(self):

        # self._metrics.count_detections(self.frame_count, self._ground_truth, self._detections)

        # this is where self.frame_count is incremented
        super().draw_frame()

    def end(self):
        super().end()

        # self._metrics.display_pr_curve(self.run_name)