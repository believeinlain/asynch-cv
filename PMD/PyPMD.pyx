# distutils: language = c++

import numpy as np
cimport numpy as np

from PersistentMotionDetector cimport *

cdef class PyPMD:
    cdef PersistentMotionDetector *cpp_PMD
    cdef xy_t width
    cdef xy_t height

    def __cinit__(self, int width, int height, param):
        self.width = width
        self.height = height

        cdef parameters c_param
        c_param.x_div = param.get('x_div', 8)
        c_param.y_div = param.get('y_div', 8)
        c_param.input_queue_depth = param.get('input_queue_depth', 64)

        self.cpp_PMD = new PersistentMotionDetector(width, height, c_param)
    
    def __dealloc__(self):
        del self.cpp_PMD

    cpdef void process_events(self, byte_t[:, :, ::1] frame, event[:] events):
        cdef int num_events = len(events)
        cdef int i, j
        cdef event e
        cdef unsigned char c

        self.cpp_PMD.process_events(&frame[0,0,0], &events[0], num_events)
        
        # detections = []

        
