
import os
from async_cv.metrics.bounding_box import BoundingBox, BBFormat, BBType
from async_cv.metrics.evaluators.pascal_voc_evaluator \
    import plot_precision_recall_curves, get_pascalvoc_metrics

from async_cv.event_processing.basic_consumer import basic_consumer


class evaluator_consumer(basic_consumer):
    def __init__(self, width, height, targets=['vessel'], show_metrics=False,
                 **kwargs):
        """Constructor

        Args:
            width (int): Width of event sensor in pixels
            height (int): Height of event sensor in pixels
            targets (list): List of targets to match against in the ground \
                truth annotations
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

    def end(self):
        super().end()

        if not self._ground_truth:
            print('Metrics not computed due to no valid targets.')
            return

        # evaluate metrics
        metrics = get_pascalvoc_metrics(
            self._ground_truth, self._detections, 0.05)
        plot_precision_recall_curves(
            metrics['per_class'],
            showAP=True,
            showInterpolatedPrecision=True,
            savePath=f'output/metrics/{self._run_name}',
            showGraphic=self._show_metrics
        )

        print('Average precision for target:', f'{metrics["mAP"]*100:0.2f}%')
        print(
            f'Precision x Recall curve saved in "output/metrics/{self._run_name}"')

    def save_ground_truth(self, label, xtl, ytl, xbr, ybr):
        if any(target in label for target in self._targets) and 'difficult' not in label:
            self._ground_truth.append(BoundingBox(f'frame_{self._frame_count:03d}',
                                                  class_id='target', coordinates=(xtl, ytl, xbr, ybr), format=BBFormat.XYX2Y2))

    def save_detection(self, conf, x, y, w, h):
        self._detections.append(BoundingBox(f'frame_{self.frame_count:03d}',
                                            class_id='target', coordinates=(x, y, w, h), format=BBFormat.XYWH,
                                            bb_type=BBType.DETECTED, confidence=conf))
