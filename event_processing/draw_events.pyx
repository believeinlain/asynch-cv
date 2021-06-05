# cython boundscheck=False
# cython wraparound=False

import numpy as np
cimport numpy as np
from types cimport *

cpdef np.ndarray[color_t, ndim=3] draw_events(
            np.ndarray[color_t, ndim=3] frame, 
            event_t[:] event_buffer
        ):
    cdef int num_events = len(event_buffer)
    cdef int i
    cdef event_t e
    cdef color_t color

    for i in range(num_events):
        e = event_buffer[i]
        color = e.p*255
        frame[e.y, e.x, 0] = color
        frame[e.y, e.x, 1] = color
        frame[e.y, e.x, 2] = color
    
    return frame