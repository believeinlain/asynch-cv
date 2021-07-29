
import os

import numpy as np
import sklearn.metrics
import matplotlib.pyplot as plt

from async_cv.event_processing.basic_consumer import basic_consumer


class evaluator_consumer(basic_consumer):
    """Consumer class for assessing the performance of detection algorithms \

    save_detection() should be called by the detector class to register a \
    detection bounding box for evaluation. Once end() is called the \
    performance metrics will be calculated for the entire run.

    """

    def __init__(self, width, height, targets=['vessel'], show_metrics=False,
                 **kwargs):
        """Constructor

        Args:
            width (int): Width of event sensor in pixels
            height (int): Height of event sensor in pixels
            targets (list): List of targets labels to match against in the \
                ground truth annotations
            show_metrics (bool): Display metrics at the end of the run

        """
        super().__init__(width, height, **kwargs)

        # ground truth gathered from annotations
        self._ground_truth = []
        # detections to collect if objects are detected
        self._detections = []
        # what kind of objects will we check against?
        self._targets = targets

        self._show_metrics = show_metrics

        # create output directories if necessary
        if not os.path.isdir(f'output/metrics/{self._run_name}'):
            os.makedirs(f'output/metrics/{self._run_name}')

    def init_frame(self, frame_buffer=None):
        super().init_frame(frame_buffer)

        # initialize ground truth list for this frame
        self._ground_truth.append([])
        # initialize detection list for this frame
        self._detections.append([])

        # read annotations
        for i in range(len(self._annotations)):
            box_frames = list(self._annotations[i]['box'])
            label = self._annotations[i]['@label']

            # sync properly to frame number
            is_in_frame = False
            for box in box_frames:
                if int(box['@frame']) == self._frame_count:
                    is_in_frame = True
                    break
            if not is_in_frame:
                continue

            # read box info
            xtl = int(float(box['@xtl']))
            ytl = int(float(box['@ytl']))
            xbr = int(float(box['@xbr']))
            ybr = int(float(box['@ybr']))

            # save the ground truth bb if applicable
            self.save_ground_truth(label, xtl, ytl, xbr, ybr)

    def end(self):
        super().end()

        if not self._ground_truth:
            print('Metrics not computed due to no valid targets.')
            return

        def intersects(bb1, bb2):
            x1, y1, w1, h1 = bb1
            x2, y2, w2, h2 = bb2
            return not ((x1 > x2+w2) or (x1+w1 < x2)
                        or (y1 > y2+h2) or (y1+h1 < y2))

        # initialize with a true negative so that ROC is defined even
        # if there are no false positives
        metrics_truth = [0]
        metrics_conf = [0]

        # evaluate metrics
        print('Evaluating metrics...')
        for frame in range(self._frame_count):
            gts = self._ground_truth[frame]
            dets = self._detections[frame]
            # print(f'Analyzing frame {frame}: \
            #     {len(gts)} targets, {len(dets)} detections.')
            # iterate through ground truth for this frame
            for gt_i, gt in enumerate(gts):
                best_conf = 0.00
                best_det = 0
                # get highest conf det that overlaps gt
                for det_i, det in enumerate(dets):
                    if not det['is_matched'] and intersects(gt['bb'], det['bb']):
                        if det['conf'] > best_conf:
                            gt['is_detected'] = True
                            best_conf = det['conf']
                            best_det = det_i
                # if we had an overlap, consider it a tentative true positive
                if gt['is_detected']:
                    # print(f'TP: target {gt_i} matched with det {best_det}, conf: {best_conf}.')
                    dets[best_det]['is_matched'] = True
                    metrics_truth.append(1)
                    metrics_conf.append(best_conf)
                # otherwise we have a false negative
                else:
                    # print(f'FN: target {gt_i} undetected.')
                    metrics_truth.append(1)
                    metrics_conf.append(0)

            # find unmatched detections
            for det_i, det in enumerate(dets):
                if not det['is_matched']:
                    is_redundant = False
                    # ignore if it falls on a gt, since we don't want to
                    # penalize redundant detections
                    for gt_i, gt in enumerate(gts):
                        if intersects(gt['bb'], det['bb']):
                            is_redundant = True
                            # print(f'Redundant det {det_i} on target {gt_i}, ignored.')
                    # if it does not overlap any gt, consider it a false positive
                    if not is_redundant:
                        # print(f'FP: det {det_i} unmatched, conf: {det["conf"]}.')
                        metrics_truth.append(0)
                        metrics_conf.append(det['conf'])

        metrics_truth_array = np.array(metrics_truth)
        metrics_conf_array = np.array(metrics_conf)

        precision, recall, _ = sklearn.metrics.precision_recall_curve(
            metrics_truth_array, metrics_conf_array
        )
        fpr, tpr, _ = sklearn.metrics.roc_curve(
            metrics_truth_array, metrics_conf_array
        )
        ap = sklearn.metrics.average_precision_score(
            metrics_truth_array, metrics_conf_array
        )
        auc_roc = sklearn.metrics.roc_auc_score(
            metrics_truth_array, metrics_conf_array
        )
        disp = sklearn.metrics.PrecisionRecallDisplay(precision, recall)
        disp.plot()
        disp.ax_.set_title(f'Average Precision: {ap:0.2f}')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.savefig(f'output/metrics/{self._run_name}/prc.png')
        if self._show_metrics:
            plt.show()

        disp = sklearn.metrics.RocCurveDisplay(fpr=fpr, tpr=tpr)
        disp.plot()
        disp.ax_.set_title(f'Area Under Curve: {auc_roc:0.2f}')
        plt.savefig(f'output/metrics/{self._run_name}/roc.png')
        if self._show_metrics:
            plt.show()

        print(f'Plots saved in "output/metrics/{self._run_name}"')

    def save_ground_truth(self, label, xtl, ytl, xbr, ybr):
        if any(target in label for target in self._targets) and 'difficult' not in label:
            self._ground_truth[self._frame_count].append({
                'bb': (xtl, ytl, xbr-xtl, ybr-ytl),
                'is_detected': False
            })

    def save_detection(self, conf, x, y, w, h):
        self._detections[self._frame_count].append({
            'conf': conf,
            'bb': (x, y, w, h),
            'is_matched': False
        })
