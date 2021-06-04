# cython: profile=True

import numpy as np
cimport numpy as np

cimport cython

ctypedef np.uint8_t COLOR_t 
ctypedef np.uint16_t XY_t 
ctypedef short P_t 

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False) # turn off negative index wrapping for entire function
def draw_events(
            np.ndarray[COLOR_t, ndim=3] frame, 
            int num_events,
            XY_t[:] x_buffer,
            XY_t[:] y_buffer,
            P_t[:] p_buffer
        ):
    cdef int i
    cdef XY_t x, y
    cdef P_t p
    cdef COLOR_t color

    for i in range(num_events):
        x = x_buffer[i]
        y = y_buffer[i]
        p = p_buffer[i]
        color = p*255
        frame[y, x, 0] = color
        frame[y, x, 1] = color
        frame[y, x, 2] = color
    
    return frame