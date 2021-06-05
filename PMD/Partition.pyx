# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True

from libc.stdlib cimport malloc, free

cdef class Partition:
    def __init__(self, xy_t width, xy_t height, xy_t x_div, xy_t y_div):
        self._width = width
        self._height = height
        self._x_div = x_div
        self._y_div = y_div

        cdef xy_t i

        self._x_boundaries = <xy_t*> malloc((x_div-1)*sizeof(xy_t))
        for i in range(0, x_div-1):
            self._x_boundaries[i] = (height/x_div)*(i+1)

        self._y_boundaries = <xy_t*> malloc((y_div-1)*sizeof(xy_t))
        for i in range(0, y_div-1):
            self._y_boundaries[i] = (height/y_div)*(i+1)

    def __dealloc__(self):
        free(self._x_boundaries)
        free(self._y_boundaries)

    cdef point_t place_event(self, xy_t x, xy_t y):
        cdef point_t dest
        cdef xy_t i

        for i in range(self._x_div-1):
            if self._x_boundaries[i] > x:
                break
            i = i + 1
        dest.x = i
        
        for i in range(self._y_div-1):
            if self._y_boundaries[i] > y:
                break
            i = i + 1
        dest.y = i

        return dest
