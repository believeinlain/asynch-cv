# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True

import numpy as np
from libc.stdlib cimport malloc, free

cdef class PersistentMotionDetector:
    def __init__(self, xy_t width, xy_t height, parameters=None):
        # create empty dict if no parameters passed
        if parameters is None:
            parameters = {}
        
        self._x_div = parameters.get('x_div', 8)
        self._y_div = parameters.get('y_div', 8)
        self._input_queue_depth = parameters.get('input_queue_depth', 64)
        self._event_buffer_depth = parameters.get('event_buffer_depth', 4)
        self._num_cluster_analyzers = parameters.get('num_cluster_analyzers', 8)

        self._width = width
        self._height = height

        self._partition = Partition(width, height, self._x_div, self._y_div)
        self._input_queues = <InputQueue_t*>malloc(self._x_div*self._y_div*sizeof(InputQueue_t))

        cdef int i, j
        for i in range(self._x_div):
            for j in range(self._y_div):
                self._input_queues[i + j*self._x_div] = InputQueue.init(self._input_queue_depth)

    cpdef np.ndarray[color_t, ndim=3] process_events(self,
            np.ndarray[color_t, ndim=3] frame, event_t[:] event_buffer):
        cdef int num_events = len(event_buffer)
        cdef int i
        cdef event_t e
        cdef color_t color
        cdef point_t placement

        # sort incoming events
        for i in range(num_events):
            e = event_buffer[i]
            place = self._partition.place_event(e.x, e.y)
            InputQueue.push(&self._input_queues[place.x + place.y*self._x_div], e)
        
        # process input queues
        for i in range(self._x_div*self._y_div):
            while not InputQueue.is_empty(&self._input_queues[i]):
                e = InputQueue.pop(&self._input_queues[i])
                color = e.p*255
                frame[e.y, e.x, 0] = color
                frame[e.y, e.x, 1] = color
                frame[e.y, e.x, 2] = color
        
        return frame

    def __dealloc__(self):
        for i in range(self._x_div*self._y_div):
            InputQueue.dealloc(&self._input_queues[i])
        free(self._input_queues)
    
    # def tick_all(self, sys_time, event_callback, cluster_callback):
    #     # cycle through each event handler
    #     for i in range(self._x_div):
    #         for j in range(self._y_div):
    #             self._event_handler[i, j].tick(sys_time, event_callback)
    #     # run the cluster prioritizer
    #     self._cluster_priority_module.tick()
    #     # cycle through each cluster analyzer
    #     for analyzer in self._cluster_analyzers:
    #         analyzer.tick(sys_time, cluster_callback)

