# pyright: reportMissingImports=false

import cv2
import numpy as np
from math import sqrt, exp

from event_processing import basic_consumer
from PMD import PyPMD


class pmd_consumer(basic_consumer):
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)

        # Process arguments
        self._filetype = self._consumer_args.get('filetype', '.raw')

        self.p = self._consumer_args.get('parameters', {})
        self.max_cluster_size = self.p.get('max_cluster_size', 50)
        
        # explicitly set types to ensure consistency between modules
        types = {}

        # get needed types to set colors
        # self._cluster_color_t = types.get('cluster_color_t', 'u1')
        # self._cluster_id_t = types.get('cluster_id_t', 'u2')
        # self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        # self._max_clusters = self._unassigned + 1
        # pick a different color for each region
        # self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        # self._max_clusters = self._unassigned + 1
        # self._cluster_color = np.zeros((self._max_clusters, 3), dtype=self._cluster_color_t)
        # for i in range(self._max_clusters):
        #     self._cluster_color[i] = np.multiply(255.0, 
        #         hsv_to_rgb((i*np.pi % 3.6)/3.6, 1.0, 1.0), casting='unsafe')

        self._pmd = PyPMD.PyPMD(width, height, self.p)

        # self._metrics = DetectionMetrics(['boat', 'RHIB'])
        # self._detections = []
    
    def process_event_buffer(self, ts, event_buffer):
        # we don't care about ts
        del ts
        # create a buffer to write cids on
        indices = np.ascontiguousarray(np.full((self.height, self.width), -1, dtype='u2'))
        # pass events to the pmd to draw
        detections = self._pmd.process_events(self.frame_to_draw, event_buffer, indices)

        active = [det for det in detections if det['is_active']]

        for det in active:
            det['image'] = np.equal(indices, det['cid'])

        r = self.max_cluster_size
        
        # merge positive detections bounding boxes together
        for a in active:
            for b in active:
                if a['is_positive'] and b['is_positive']:
                    if abs(a['x'] - b['x']) <= r*2 and abs(a['y'] - b['y']) <= r*2:
                        a['image'] = b['image'] = np.logical_or(a['image'], b['image'])
                        # if a['stability'] > 0 and b['stability'] > 0:
                        #     a['stability'] += b['stability']
                        #     b['stability'] = 0

        for det in active:
            (px, py) = (det['x'], det['y'])
            
            frame = self.frame_to_draw
            color = (det['b'], det['g'], det['r'])
            th = 1

            scale = 5
            
            cv2.arrowedLine(frame, (px, py), (int(px+det['long_v_x']*scale), int(py+det['long_v_y']*scale)), color, th)
            cv2.arrowedLine(frame, (px, py), (int(px+det['short_v_x']*scale), int(py+det['short_v_y']*scale)), color, th)

            diamond_color = tuple(np.multiply(0.5, color))
            cv2.line(frame, (px, py-r), (px+r, py), diamond_color, th)
            cv2.line(frame, (px+r, py), (px, py+r), diamond_color, th)
            cv2.line(frame, (px, py+r), (px-r, py), diamond_color, th)
            cv2.line(frame, (px-r, py), (px, py-r), diamond_color, th)

            if det['is_positive']:
                image = np.multiply(255, det['image'], dtype='u1')
                x, y, w, h = cv2.boundingRect(image)
                conf = 1-exp(-0.0005*det['stability'])
                if det['stability'] > 0 and conf > 0.5:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255,255,255), 1)
                    cv2.putText(frame, f"{conf:0.2f}", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), th, cv2.LINE_AA)

            cv2.circle(frame, (px, py), int(min(det['ratio']*0.1,10)*scale), color, th)
        
    def end(self):
        super().end()