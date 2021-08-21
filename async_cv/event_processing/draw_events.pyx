"""Cython extension for drawing a buffer of events onto the screen.
"""

import numpy as np
cimport numpy as np


ctypedef unsigned char byte_t

cdef struct event:
    unsigned short x, y
    short p
    long long t

def draw_events(byte_t[:, :, ::1] frame, event[:] event_buffer):
    """Draw the events in event_buffer onto frame.

    Args:
        frame: A 3D memoryview of shape (width, height, 3) for BGR color \
            channels of each pixel. Each color is an unsigned char (byte_t).
        event_buffer: A memoryview of event structs. Data types for the event \
            struct must match the type passed to the consumer in play_file.py.

    """
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