
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
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._cluster_color_t = types.get('cluster_color_t', 'u1')
        self._timestamp_t = types.get('timestamp_t', 'u8')
        self._cluster_id_t = types.get('cluster_id_t', 'u2')
        self._xy_t = types.get('xy_t', 'u2')
        # self._vector_t = types.get('vector_t', 'i2')
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
        if self._id == self._unassigned:
            new_id = self._cluster_priority_module.get_next_target()
            self.reassign_id(new_id)

        weight = self._cluster_buffer.get_weight(self._id)
        if weight == 0:
            self._cluster_priority_module.unassign_target(self._id)
            self._id = self._unassigned
            return
        
        centroid = np.array(self._cluster_buffer.get_centroid_f(self._id), dtype=self._precision_xy_t)
        int_c = np.array(centroid, dtype=self._xy_t)
        # birth_time = self._cluster_buffer.get_birth(self._id)

        # update region profile
        self._profile_top = (self._profile_top + 1) % self._profile_length
        self._profile_timestamps[self._profile_top] = sys_time
        self._profile_centroids[self._profile_top] = centroid

        current = np.where(self._profile_timestamps > 0)[0]
        order = np.argsort(self._profile_timestamps[current])
        past_locations = np.array(self._profile_centroids[current][order])
        path_steps = np.diff(past_locations, axis=0)
        # print('path_steps', path_steps)

        # init callback variables
        endpoint = None
        radius = None
        conf = 0

        # TODO: Fix overflow runtime errors:
        # Frame time: 240/30(ms) C:\Users\GML LAB\AppData\Local\Programs\Python\Python37\lib\site-packages\numpy\core\fromnumeric.py:87: RuntimeWarning: overflow encountered in reduce
        # return ufunc.reduce(obj, axis, dtype, out, **passkwargs)
        # c:\dev\asynch-cv\PMD\ClusterAnalyzer.py:91: RuntimeWarning: invalid value encountered in half_scalars
        # delta = (displacement_length/path_length)/ratio_th - 1
        # Frame time: 238/30(ms) c:\dev\asynch-cv\PMD\ClusterAnalyzer.py:80: RuntimeWarning: overflow encountered in square
        # displacement_length = np.sqrt(np.sum(np.square(displacement)))
        # Frame time: 225/30(ms) c:\dev\asynch-cv\PMD\ClusterAnalyzer.py:76: RuntimeWarning: overflow encountered in square
        # path_length = np.sqrt(np.sum(np.square(path_steps))) # this doesn't really make sense, but works
        if path_steps.size > 0:
            path_traveled = np.sum(np.abs(path_steps), axis=0)
            # path_length = np.sqrt(np.sum(np.square(path_traveled))) # this makes sense, but doesn't really work
            path_length = np.sqrt(np.sum(np.square(path_steps))) # this doesn't really make sense, but works
            # print('path_length', path_length)
            displacement = np.sum(path_steps, axis=0)
            # print('displacement', displacement)
            displacement_length = np.sqrt(np.sum(np.square(displacement)))

            if path_length > 0:
                scale = 10
                ratio_th = 3

                endpoint = np.sum([int_c, np.array(scale*(displacement/path_length))], axis=0)
                # endpoint = np.sum([int_c, np.array(scale*(displacement))], axis=0, dtype=self._xy_t)
                # print('endpoint', endpoint)
                radius = int(scale*ratio_th)

                delta = (displacement_length/path_length)/ratio_th - 1
                if self._stability + delta > 0:
                    self._stability += delta

                tau = -0.05
                conf = 1 - exp(tau*self._stability)

        # binary image representing all locations belonging to this region
        # for cv2 image processing analysis
        image = np.multiply(255, np.transpose(self._event_buffer.get_cluster_map(self._id)), dtype=self._cluster_color_t)

        # find the bounding box
        bb = cv2.boundingRect(image)

        cluster_callback(self._id, int_c, weight, conf, bb, endpoint, radius)
    
    def reassign_id(self, id):
        self._id = id
        self._profile_centroids = np.zeros((self._profile_length, 2), dtype=self._precision_xy_t)
        self._profile_timestamps = np.zeros(self._profile_length, dtype=self._timestamp_t)
        self._profile_top = 0
        self._stability = 0