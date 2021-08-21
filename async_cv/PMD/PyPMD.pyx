
import numpy as np
cimport numpy as np

from async_cv.PMD.PersistentMotionDetector cimport *


cdef class PyPMD:
    cdef PersistentMotionDetector *_cpp_PMD
    cdef xy_t _width, _height
    cdef int _num_detections

    def __cinit__(self, xy_t width, xy_t height, param):
        self._width = width
        self._height = height

        # read input parameters and set appropriate values for the struct
        cdef parameters c_param
        c_param.width = width
        c_param.height = height
        c_param.x_div = param.get('x_div', 8)
        c_param.y_div = param.get('y_div', 8)
        c_param.us_per_event = param.get('us_per_event', 0)
        c_param.temporal_filter = param.get('temporal_filter', 5000)
        c_param.event_buffer_depth = param.get('event_buffer_depth', 4)
        c_param.tf = param.get('tf', 200_000)
        c_param.tc = param.get('tc', 200_000)
        c_param.n = param.get('n', 5)
        c_param.buffer_flush_period = param.get('buffer_flush_period', 1_000)
        c_param.max_cluster_size = param.get('max_cluster_size', 50)
        c_param.num_analyzers = param.get('num_analyzers', 8)
        c_param.sample_period = param.get('sample_period', 10_000)
        c_param.long_duration = param.get('long_duration', 2_000_000)
        c_param.short_duration = param.get('short_duration', 1_000_000)
        c_param.ratio_threshold = param.get('ratio_threshold', 20)
        c_param.dot_ratio_threshold = param.get('dot_ratio_threshold', 0.9)
        c_param.ratio_stability_factor = param.get('ratio_stability_factor', 1.0)
        c_param.dot_ratio_stability_factor = param.get('dot_ratio_stability_factor', 1.0)

        self._num_detections = c_param.num_analyzers

        self._cpp_PMD = new PersistentMotionDetector(c_param)
    
    def __dealloc__(self):
        del self._cpp_PMD

    cpdef detection[:] process_events(self, byte_t[:, :, ::1] frame, 
                                      event[:] events, cid_t[:, ::1] indices):
        cdef unsigned int num_events = <unsigned int>len(events)

        # allocate results array
        cdef np.ndarray result_array = np.ndarray((self._num_detections,), dtype=[
            ('is_active', int), 
            ('x', int), ('y', int), 
            ('r', int), ('g', int), ('b', int),
            ('cid', int),
            ('long_v_x', np.float32), ('long_v_y', np.float32),
            ('short_v_x', np.float32), ('short_v_y', np.float32),
            ('stability', int),
            ('ratio', np.float32), ('dot_ratio', np.float32)
        ])
        cdef detection[:] results = result_array

        # make calls to C++
        self._cpp_PMD.initFramebuffer(&frame[0,0,0])
        self._cpp_PMD.simulate(&events[0], num_events, &results[0], &indices[0,0])

        # return the results
        return results
