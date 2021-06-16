# pyright: reportMissingImports=false

import cv2
import numpy as np
from math import sqrt, exp
from copy import copy

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
        results = self._pmd.process_events(self.frame_to_draw, event_buffer, indices)

        r = self.max_cluster_size
        frame = self.frame_to_draw
        scale = 5
        tau = -0.0008

        # filter out inactive results
        active = [res for res in results if res['is_active']]

        # draw results from cluster analyzers
        for a in active:
            a['is_dup'] = False
            (px, py) = (a['x'], a['y'])
            color = (a['b'], a['g'], a['r'])

            # draw diamond representing max cluster size
            diamond_color = tuple(np.multiply(0.5, color))
            cv2.line(frame, (px, py-r), (px+r, py), diamond_color, 1)
            cv2.line(frame, (px+r, py), (px, py+r), diamond_color, 1)
            cv2.line(frame, (px, py+r), (px-r, py), diamond_color, 1)
            cv2.line(frame, (px-r, py), (px, py-r), diamond_color, 1)

            # draw short-term and long-term velocities
            cv2.arrowedLine(frame, (px, py), (int(px+a['long_v_x']*scale), int(py+a['long_v_y']*scale)), color, 1)
            cv2.arrowedLine(frame, (px, py), (int(px+a['short_v_x']*scale), int(py+a['short_v_y']*scale)), color, 1)

            # draw the velocity ratio
            cv2.circle(frame, (px, py), int(0.1*min(a['ratio'],self.p['ratio_threshold'])*scale), color, 1)

            # save footprint as a boolean image
            a['image'] = np.equal(indices, a['cid'])

            # calculate confidence to determine if positive
            a['conf'] = 1-exp(tau*a['stability'])
        
        # filter out negative results
        positive = [a for a in active if a['conf'] > 0.5]

        detections = []

        # merge based on proximity
        for a in positive:
            for b in positive[positive.index(a)+1:]:
                if abs(a['x'] - b['x']) <= r*2 and abs(a['y'] - b['y']) <= r*2:
                    a['image'] = np.logical_or(a['image'], b['image'])
                    a['stability'] += b['stability']
                    b['is_dup'] = True
            
            # combined = {
            #     'image': a['image'],
            #     'stability': a['stability']
            # }
            # for b in overlaps:
            #     combined['image'] = np.logical_or(combined['image'], b['image'])
            #     combined['stability'] += b['stability']

            # image = np.multiply(255, combined['image'], dtype='u1')
            # combined['bb'] = cv2.boundingRect(image)
            # detections.append(combined)

        def intersect(bb1, bb2):
            x1, y1, w1, h1 = bb1
            x2, y2, w2, h2 = bb2
            return x1 < x2+w2 and x1+w1 > x2 and \
                y1 < y2+h2 and y1+h1 > y2
        
        detections = [d for d in positive if not d['is_dup']]

        detection_bb = set()

        # merge based on bb overlaps
        # for a in detections:
        #     overlaps = []
        #     for b in detections:
        #         if intersect(a['bb'], b['bb']):
        #             overlaps.append(b)
            
        #     combined = {
        #         'image': a['image'],
        #         'stability': a['stability']
        #     }
        #     for b in overlaps:
        #         combined['image'] = np.logical_or(combined['image'], b['image'])
        #         combined['stability'] += b['stability']

        #     image = np.multiply(255, combined['image'], dtype='u1')
        #     bb = cv2.boundingRect(image)
            
        #     detection_bb[bb] = combined

        for d in detections:
            image = np.multiply(255, d['image'], dtype='u1')
            x, y, w, h = cv2.boundingRect(image)
            conf = 1-exp(tau*d['stability'])
            if conf > 0.5:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255,255,255), 1)
                cv2.putText(frame, f"{conf:0.2f}", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1, cv2.LINE_AA)

    def end(self):
        super().end()