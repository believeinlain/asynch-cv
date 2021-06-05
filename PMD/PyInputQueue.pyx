# distutils: language = c++

from types cimport *

from InputQueue cimport InputQueue

cdef class PyInputQueue:
    cdef InputQueue *cpp_queue

    def __cinit__(self, int depth):
        self.cpp_queue = new InputQueue(depth)
    
    def __dealloc__(self):
        del self.cpp_queue

    cpdef void push(self, event_t e):
        self.cpp_queue.push(e)

    cpdef bool pop(self, event_t out):
        return self.cpp_queue.pop(out)
