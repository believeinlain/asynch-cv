
from types cimport *

cdef extern from "InputQueue.cpp":
    pass

cdef extern from "InputQueue.h" namespace "PMD":
    cdef cppclass InputQueue:
        InputQueue(int depth)
        int depth, count, front, back
        event_t *queue

        void push(event_t e)
        bool pop(event_t &out)