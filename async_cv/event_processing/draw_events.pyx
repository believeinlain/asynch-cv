
import numpy as np
cimport numpy as np

ctypedef unsigned char byte_t

cdef struct event:
    unsigned short x, y
    short p
    long long t

def draw_events(byte_t[:, :, ::1] frame, event[:] event_buffer):
    """ Draw the events in event_buffer onto frame """
    cdef int num_events = len(event_buffer)

    # draw events colored by polarity
    cdef event e
    cdef unsigned char color
    for i in range(num_events):
        e = event_buffer[i]
        color = e.p*255
        frame[e.y, e.x, 0] = color
        frame[e.y, e.x, 1] = color
        frame[e.y, e.x, 2] = color