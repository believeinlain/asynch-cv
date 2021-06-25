
from sys import stdout
import cv2
import numpy as np
from math import exp
from time import time

from async_cv.event_processing.evaluator_consumer import evaluator_consumer
from async_cv.PMD import PyPMD


class pmd_consumer(evaluator_consumer):

    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)

        # Process arguments
        self._filetype = consumer_args.get('filetype', '.raw')

        self.p = consumer_args.get('parameters', {})
        self.max_cluster_size = self.p.get('max_cluster_size', 50)

        self._pmd = PyPMD.PyPMD(width, height, self.p)

        # create a buffer to write cids on
        self._cluster_map = np.ascontiguousarray(
            np.full((height, width), -1, dtype='u2'))

    def process_event_buffer(self, ts, event_buffer):
        # we don't care about ts
        del ts
        
        start = time()
        
        # pass events to the pmd to draw
        results = self._pmd.process_events(
            self._frame_to_draw, event_buffer, self._cluster_map)
        
        ms = (time() - start)*1000.0

        r = self.max_cluster_size
        frame = self._frame_to_draw
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
            cv2.arrowedLine(frame, (px, py), (int(
                px+a['long_v_x']*scale), int(py+a['long_v_y']*scale)), color, 1)
            cv2.arrowedLine(frame, (px, py), (int(
                px+a['short_v_x']*scale), int(py+a['short_v_y']*scale)), color, 1)

            # draw the velocity ratio
            cv2.circle(frame, (px, py), int(
                0.1*min(a['ratio'], self.p['ratio_threshold'])*scale), color, 1)

            # save footprint as a boolean image
            a['image'] = np.equal(self._cluster_map, a['cid'])

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

        # remove dupes after merging
        detections = [p for p in positive if not p['is_dup']]

        # compute bb for each detection
        for d in detections:
            d['bb'] = cv2.boundingRect(
                np.multiply(255, d['image'], dtype='u1'))

        def is_intersect(bb1, bb2):
            x1, y1, w1, h1 = bb1
            x2, y2, w2, h2 = bb2
            return not ((x1 > x2+w2) or (x1+w1 < x2)
                        or (y1 > y2+h2) or (y1+h1 < y2))

        # merge based on bb
        for a in detections:
            for b in detections[detections.index(a)+1:]:
                if is_intersect(a['bb'], b['bb']):
                    a['image'] = np.logical_or(a['image'], b['image'])
                    a['stability'] += b['stability']
                    b['is_dup'] = True

        # remove dupes after merging
        detections = [d for d in detections if not d['is_dup']]

        for d in detections:
            image = np.multiply(255, d['image'], dtype='u1')
            x, y, w, h = cv2.boundingRect(image)
            conf = 1-exp(tau*d['stability'])
            if conf > 0.5:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
                cv2.putText(frame, f"{conf:0.2f}", (x, y),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)

                # record the detection for metrics
                self.save_detection(conf, x, y, w, h)

        stdout.write(f' PMD processed {len(event_buffer)} events in {ms:.0f}ms.')
        stdout.flush()
