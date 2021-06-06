
import numpy as np
cimport numpy as np

from PMD.PersistentMotionDetector cimport *

cdef class PyPMD:
    cdef PersistentMotionDetector *cpp_PMD
    cdef xy_t width, height
    cdef timestamp_t cycle_period_us

    def __cinit__(self, int width, int height, param):
        self.width = width
        self.height = height

        cdef parameters c_param
        c_param.x_div = param.get('x_div', 8)
        c_param.y_div = param.get('y_div', 8)
        c_param.input_queue_depth = param.get('input_queue_depth', 64)
        c_param.event_handler_us_per_event = param.get('event_handler_us_per_event', 0)

        self.cycle_period_us = param.get('cycle_period_us', 1000)

        self.cpp_PMD = new PersistentMotionDetector(width, height, c_param)
    
    def __dealloc__(self):
        del self.cpp_PMD

    cpdef void process_events(self, byte_t[:, :, ::1] frame, event[:] events):
        cdef int num_events = len(events)
        cdef int i, j
        cdef event e
        cdef unsigned char c

        self.cpp_PMD.init_framebuffer(&frame[0,0,0])
        cdef timestamp_t start_time = events[0].t
        cdef timestamp_t end_time = events[num_events-1].t+1
        cdef timestamp_t interval = self.cycle_period_us

        cdef int last_index = 0
        for time in range(start_time, end_time, interval):
            last_index = self.cpp_PMD.input_events_until(time, &events[0], num_events, last_index)
            self.cpp_PMD.process_until(time)
        self.cpp_PMD.input_events_until(end_time, &events[0], num_events, last_index)
        self.cpp_PMD.process_until(end_time)

        