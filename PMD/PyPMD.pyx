
import numpy as np
cimport numpy as np

from PMD.PersistentMotionDetector cimport *

cdef class PyPMD:
    cdef PersistentMotionDetector *cpp_PMD
    cdef xy_t width, height

    def __cinit__(self, xy_t width, xy_t height, param):
        self.width = width
        self.height = height

        cdef parameters c_param
        c_param.x_div = param.get('x_div', 8)
        c_param.y_div = param.get('y_div', 8)
        c_param.us_per_event = param.get('us_per_event', 0)
        c_param.event_buffer_depth = param.get('event_buffer_depth', 4)
        c_param.tf = param.get('tf', 200_000)
        c_param.tc = param.get('tc', 200_000)
        c_param.n = param.get('n', 5)
        c_param.buffer_flush_period = param.get('buffer_flush_period', 1_000)

        self.cpp_PMD = new PersistentMotionDetector(width, height, c_param)
    
    def __dealloc__(self):
        del self.cpp_PMD

    cpdef void process_events(self, byte_t[:, :, ::1] frame, event[:] events):
        cdef unsigned int num_events = len(events)

        self.cpp_PMD.init_framebuffer(&frame[0,0,0])
        self.cpp_PMD.process_events(&events[0], num_events)

        
