
from types cimport *

cdef class Partition:
    cdef xy_t _x_div
    cdef xy_t _y_div

    cdef xy_t _width
    cdef xy_t _height

    cdef xy_t *_x_boundaries
    cdef xy_t *_y_boundaries

    cdef point_t place_event(self, xy_t x, xy_t y)
