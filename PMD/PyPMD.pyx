
import numpy as np
cimport numpy as np

from PMD.PersistentMotionDetector cimport *

cdef class PyPMD:
    cdef PersistentMotionDetector *cpp_PMD
    cdef xy_t width, height

    def __cinit__(self, int width, int height, param):
        self.width = width
        self.height = height

        cdef parameters c_param
        c_param.x_div = param.get('x_div', 8)
        c_param.y_div = param.get('y_div', 8)
        c_param.input_queue_depth = param.get('input_queue_depth', 64)
        c_param.events_per_ms = param.get('events_per_ms', 0)

        self.cpp_PMD = new PersistentMotionDetector(width, height, c_param)
    
    def __dealloc__(self):
        del self.cpp_PMD

    cpdef void process_events(self, byte_t[:, :, ::1] frame, event[:] events):
        cdef int num_events = len(events)
        cdef int i, j
        cdef event e
        cdef unsigned char c

        self.cpp_PMD.init_framebuffer(&frame[0,0,0])
        self.cpp_PMD.input_events(&events[0], num_events)
        for time in range(events[0].t, events[num_events-1].t+1, 10000):
            self.cpp_PMD.process_until(time)

        
