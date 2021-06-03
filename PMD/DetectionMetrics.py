
import re
import matplotlib.pyplot as plt
import numpy as np

class DetectionMetrics:
    def __init__(self, targets):
        self._targets = targets
        self._frames = 0

        self._c_tp = 0
        self._c_fp = 0
        self._c_nt = 0

        self._pc_data = []

    def count_detections(self, frame, ground_truth, detections):
        self._frames = max(self._frames, frame)

        target_gt = []
        current_det = detections[frame]
        results = []

        for gt in ground_truth[frame]:
            for target in self._targets:
                if re.search(target, gt['label']) is not None:
                    target_gt.append(gt)

        for det in current_det:
            det['hit_target'] = False
            del det['centroid']
            del det['endpoint']

        num_targets = len(target_gt)
        tp = 0
        for t in target_gt:
            t['detections'] = 0
            results.append(t)
            for det in current_det:
                if self.is_overlapping(t['bb'], det['bb']):
                    t['detections'] += 1
                    det['hit_target'] = True
            if t['detections'] > 0:
                tp += 1

        fp = 0
        for det in current_det:
            if not det['hit_target']:
                fp += 1

        self._c_tp += tp
        self._c_fp += fp
        self._c_nt += num_targets

        precision, recall = self.get_cumulative_results()

        self._pc_data.append((precision, recall))

        print('this frame (targets/TP/FP) =', f'({num_targets}/{tp}/{fp})', 
        'cumulative (precision/recall) =', f'({precision}/{recall})')

    def display_pr_curve(self, title):
        points = np.array(self._pc_data)
        plt.plot(points[:, 1], points[:, 0])
        plt.title(title)
        plt.ylabel('Precision')
        plt.xlabel('Recall')
        plt.xlim(0.0, 1.1)
        plt.ylim(0.0, 1.1)
        plt.show()

    def get_cumulative_results(self):
        precision = self._c_tp/(self._c_tp+self._c_fp) if (self._c_tp > 0) else 0
        recall = self._c_tp/self._c_nt if (self._c_nt > 0) else 0

        return precision, recall
        
    def is_overlapping(self, bb1, bb2):
        xtl1, ytl1, xbr1, ybr1 = bb1
        xtl2, ytl2, xbr2, ybr2 = bb2

        dx = min(xbr1, xbr2) - max(xtl1, xtl2)
        dy = min(ybr1, ybr2) - max(ytl1, ytl2)

        return (dx>=0) and (dy>=0)