
from math import exp
import cv2
import numpy as np
from PMD.ClusterBuffer import *
from PMD.ClusterPriorityModule import *
from PMD.EventBuffer import *

class ClusterAnalyzer:
    def __init__(self, priority, cluster_priority_module: ClusterPriorityModule, cluster_buffer: ClusterBuffer, event_buffer: EventBuffer, parameters=None, types=None):
        # create empty dict if no parameters passed
        if parameters is None:
            parameters = {}
        # set parameters
        self._profile_length = parameters.get('cluster_profile_length', 32)
        self._stability_threshold = parameters.get('stability_threshold', 3.0)
        self._stability_rate = parameters.get('stability_rate', 0.05)
        self._confidence_threshold = parameters.get('confidence_threshold', 0.75)
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._cluster_color_t = types.get('cluster_color_t', 'u1')
        self._timestamp_t = types.get('timestamp_t', 'u8')
        self._cluster_id_t = types.get('cluster_id_t', 'u2')
        self._xy_t = types.get('xy_t', 'u2')
        self._precision_xy_t = types.get('precision_xy_t', 'f2')

        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._priority = priority
        self._id = self._unassigned
        self._cluster_priority_module = cluster_priority_module
        self._cluster_buffer = cluster_buffer
        self._event_buffer = event_buffer

        # establish arrays to profile region movement over time
        self._profile_centroids = np.zeros((self._profile_length, 2), dtype=self._precision_xy_t)
        self._profile_timestamps = np.zeros(self._profile_length, dtype=self._timestamp_t)
        self._profile_top = 0

        # accumulate stability over time
        self._stability = 0

    def tick(self, sys_time, cluster_callback):
        """Called by PersistentMotionDetector.tick_all"""
        if self._id == self._unassigned:
            # reassign to next highest priority id
            self._id = self._cluster_priority_module.get_next_target()
            self._profile_centroids = np.zeros((self._profile_length, 2), dtype=self._precision_xy_t)
            self._profile_timestamps = np.zeros(self._profile_length, dtype=self._timestamp_t)
            self._profile_top = 0
            self._stability = 0

        if self._cluster_buffer.is_empty(self._id):
            self._cluster_priority_module.unassign_target(self._id)
            self._id = self._unassigned
            return
        
        centroid = np.array(self._cluster_buffer.get_centroid_f(self._id), dtype=self._precision_xy_t)
        int_c = np.array(centroid, dtype=self._xy_t)

        # update region profile
        self._profile_top = (self._profile_top + 1) % self._profile_length
        self._profile_timestamps[self._profile_top] = sys_time
        self._profile_centroids[self._profile_top] = centroid

        current = np.where(self._profile_timestamps > 0)[0]
        order = np.argsort(self._profile_timestamps[current])
        past_locations = np.array(self._profile_centroids[current][order])
        path_steps = np.diff(past_locations, axis=0)

        # init callback variables
        endpoint = None
        radius = None
        conf = 0.0

        if path_steps.size > 0:
            path_length = np.sqrt(np.sum(np.square(path_steps))) # this doesn't really make sense, but works
            displacement = np.sum(path_steps, axis=0)
            # TODO: RuntimeWarning: overflow encountered in square
            displacement_length = np.sqrt(np.sum(np.square(displacement)))

            if path_length > 0:
                draw_scale = 10

                endpoint = np.sum([int_c, np.array(draw_scale*(displacement/path_length))], axis=0)
                radius = int(draw_scale*self._stability_threshold)

                # TODO: RuntimeWarning: invalid value encountered in half_scalars
                delta = (displacement_length/path_length)/self._stability_threshold - 1
                if self._stability + delta > 0:
                    self._stability += delta

                conf = 1 - exp(-self._stability_rate*self._stability)

        results = {
            'is_detected': conf>self._confidence_threshold,
            'centroid': int_c,
            'confidence': conf,
            'endpoint': endpoint,
            'radius': radius
        }

        cluster_callback(self._id, results)