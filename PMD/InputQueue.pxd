
from types cimport *

cdef class InputQueue:
    cdef int _depth
    cdef event_t *_queue
    cdef int _count
    cdef int _front
    cdef int _back
    
    cdef bool is_empty(self)
    cdef void push(self, event_t event)
    cdef event_t pop(self)