
from types cimport *

cdef packed struct InputQueue_t:
    int _depth
    event_t *_queue
    int _count
    int _front
    int _back

cdef InputQueue_t init(int depth)
cdef void dealloc(InputQueue_t self)
cdef bool is_empty(InputQueue_t)
cdef void push(InputQueue_t, event_t event)
cdef event_t pop(InputQueue_t)