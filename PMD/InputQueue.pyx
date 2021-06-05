# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True

from libc.stdlib cimport malloc, free

cdef InputQueue_t init(int depth):
    cdef InputQueue_t new_queue
    new_queue._depth = depth
    new_queue._queue = <event_t*> malloc(depth*sizeof(event_t))
    new_queue._front = 0
    new_queue._back = 0
    new_queue._count = 0
    return new_queue

cdef void dealloc(InputQueue_t self):
    free(self._queue)

cdef bool is_empty(InputQueue_t self):
    return (self._count == 0)

cdef void push(InputQueue_t self, event_t event):
    self._queue[self._back] = event
    self._back = (self._back + 1) % self._depth

    if self._count < self._depth:
        self._count += 1

cdef event_t pop(InputQueue_t self):
    cdef event_t item

    if self._count > 0:
        item = self._queue[self._front]
        self._count -= 1
        self._front = (self._front + 1) % self._depth

    return item
