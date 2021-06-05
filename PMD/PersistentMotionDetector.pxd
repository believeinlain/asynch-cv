

cimport numpy as np
from types cimport *

from Partition cimport *

cdef class PersistentMotionDetector:
    cdef int _x_div
    cdef int _y_div
    cdef int _input_queue_depth
    cdef int _event_buffer_depth
    cdef int _num_cluster_analyzers

    cdef xy_t _width
    cdef xy_t _height

    cdef Partition _partition

    cpdef np.ndarray[color_t, ndim=3] process_events(self,
            np.ndarray[color_t, ndim=3] frame, event_t[:] event_buffer)