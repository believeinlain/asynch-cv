# distutils: language = c++

import numpy as np
cimport numpy as np

from PersistentMotionDetector cimport *

cdef class PyPMD:
    cdef PersistentMotionDetector *cpp_PMD
    cdef xy_t width
    cdef xy_t height

    def __cinit__(self, int width, int height, parameters param):
        self.width = width
        self.height = height
        self.cpp_PMD = new PersistentMotionDetector(width, height, param)
        
    
    def __dealloc__(self):
        del self.cpp_PMD

    def process_events(self, np.ndarray[unsigned char, ndim=3] frame, event[:] events):
        cdef int num_events = len(events)
        cdef int i, j
        cdef event e
        cdef color c

        new_frame = np.ascontiguousarray(frame)

        cdef array_2d[color] frame_array = array_2d[color](height, width, &new_frame[0,0])

        for i in range(num_events):
            e = events[i]
            c = color(e.p*255, e.p*255, e.p*255)
            frame_array.put(e.x, e.y, c)

        return new_frame
