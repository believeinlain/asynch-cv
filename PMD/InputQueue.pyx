# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True

from libc.stdlib cimport malloc, free

cdef class InputQueue:
    def __init__(self, int depth):
        self._depth = depth
        self._queue = <event_t*> malloc(depth*sizeof(event_t))
        self._count = 0
        self._front = 0
        self._back = 0

    def __dealloc__(self):
        free(self._queue)
        
    def __len__(self):
        return self._count

    cdef bool is_empty(self):
        return (self._count == 0)

    cdef void push(self, event_t event):
        self._queue[self._back] = event
        self._back = (self._back + 1) % self._depth

        if self._count < self._depth:
            self._count += 1

    cdef event_t pop(self):
        cdef event_t item

        if self._count > 0:
            item = self._queue[self._front]
            self._count -= 1
            self._front = (self._front + 1) % self._depth

        return item
