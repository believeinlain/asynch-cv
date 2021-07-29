
from sys import stdout
import cv2
import numpy as np
from math import exp
from time import time

import json

from async_cv.event_processing.evaluator_consumer import evaluator_consumer
from async_cv.PMD import PyPMD


class pmd_consumer(evaluator_consumer):
    """Consumer class for using the PersistentMotionDetector"""

    def __init__(self, width, height, **kwargs):
        super().__init__(width, height, **kwargs)

        # Process arguments
        self._filetype = kwargs.get('filetype', '.raw')

        self._p = kwargs.get('parameters', {})
        self._max_cluster_size = self._p.get('max_cluster_size', 50)
        self._detection_tau = self._p.get('detection_tau', -0.0008)

        self._pmd = PyPMD.PyPMD(width, height, self._p)

        self._log_data = {}

        # create a buffer to write cids on
        self._cluster_map = np.ascontiguousarray(
            np.full((height, width), -1, dtype='u2'))

    def process_event_buffer(self, ts, event_buffer):
        del ts
        start = time()

        # pass events to the pmd to draw
        results = self._pmd.process_events(
            self._frame_to_draw, event_buffer, self._cluster_map)

        ms = (time() - start)*1000.0

        r = self._max_cluster_size
        frame = self._frame_to_draw
        scale = 5
        tau = self._detection_tau

        # filter out inactive results
        active = [res for res in results if res['is_active']]

        # draw results from cluster analyzers
        for a in active:
            a['is_dup'] = False
            (px, py) = c = (a['x'], a['y'])
            color = (a['b'], a['g'], a['r'])

            # draw diamond representing max cluster size
            diamond_color = tuple(np.multiply(0.5, color))
            cv2.line(frame, (px, py-r), (px+r, py), diamond_color, 1)
            cv2.line(frame, (px+r, py), (px, py+r), diamond_color, 1)
            cv2.line(frame, (px, py+r), (px-r, py), diamond_color, 1)
            cv2.line(frame, (px-r, py), (px, py-r), diamond_color, 1)

            # draw short-term and long-term velocities
            cv2.arrowedLine(frame, c, (int(
                px+a['long_v_x']*scale), int(py+a['long_v_y']*scale)), color, 1)
            cv2.arrowedLine(frame, c, (int(
                px+a['short_v_x']*scale), int(py+a['short_v_y']*scale)), color, 1)

            # draw the velocity ratio
            cv2.circle(frame, c, int(
                min(a['ratio'], self._p['ratio_threshold'])*2.5), color, 1)

            # draw the velocity dot ratio
            if a['dot_ratio'] < self._p['dot_ratio_threshold']:
                markerSize = int(
                    -100.0*(a['dot_ratio'] - self._p['dot_ratio_threshold']))
                cv2.drawMarker(frame, c, color,
                               cv2.MARKER_TILTED_CROSS, markerSize)

            # save footprint as a boolean image
            a['image'] = np.equal(self._cluster_map, a['cid'])

            # calculate confidence to determine if positive
            a['conf'] = 1-exp(tau*a['stability'])

            cid_str = str(a['cid'])
            if cid_str not in self._log_data:
                self._log_data[cid_str] = []

            data_point = {}
            data_point['long_v_x'] = a['long_v_x']
            data_point['long_v_y'] = a['long_v_y']
            data_point['short_v_x'] = a['short_v_x']
            data_point['short_v_y'] = a['short_v_y']
            data_point['frame'] = self._frame_count
            data_point['conf'] = a['conf']
            data_point['is_target'] = False

            gts = self._ground_truth[self._frame_count]
            for gt in gts:
                (x, y, w, h) = gt['bb']
                if (x < px < x+w) and (y < py < y+h):
                    data_point['is_target'] = True

            self._log_data[cid_str].append(data_point)

        # filter out negative results
        detections = [a for a in active if a['conf'] > 0.0]

        for d in detections:
            image = np.multiply(255, d['image'], dtype='u1')
            x, y, w, h = cv2.boundingRect(image)
            conf = 1-exp(tau*d['stability'])

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
            cv2.putText(frame, f"{conf:0.2f}", (x, y),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)

            # record the detection for metrics
            self.save_detection(conf, x, y, w, h)

        stdout.write(
            f' PMD processed {len(event_buffer)} events in {ms:.0f}ms.')
        stdout.flush()

    def end(self):
        super().end()

        # save a json file of collected movement data for external analysis
        json.dump(self._log_data, open(f'output/{self._run_name}.json', 'w+'))
