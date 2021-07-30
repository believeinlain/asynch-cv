"""Definitions for interfacing with the PersistentMotionDetector C++ class \
through Cython.
"""

from libcpp cimport bool

cdef extern from 'types.h' namespace 'PMD':
    cdef packed struct parameters:
        int width, height
        int x_div, y_div
        int us_per_event
        int temporal_filter
        int event_buffer_depth
        int tf, tc, n
        int buffer_flush_period
        int max_cluster_size
        int num_analyzers
        int sample_period
        int long_duration
        int short_duration
        int ratio_threshold
        float dot_ratio_threshold
        float ratio_stability_factor
        float dot_ratio_stability_factor

    cdef packed struct detection:
        int is_active
        int x, y
        int r, g, b
        int cid
        float long_v_x, long_v_y
        float short_v_x, short_v_y
        int stability
        float ratio
        float dot_ratio

    ctypedef unsigned short xy_t
    ctypedef short p_t
    ctypedef long long ts_t
    ctypedef unsigned short cid_t

    cdef packed struct event:
        xy_t x, y
        p_t p
        ts_t t
        
    ctypedef unsigned char byte_t

cdef extern from 'PersistentMotionDetector.h' namespace 'PMD':
    cdef cppclass PersistentMotionDetector:
        PersistentMotionDetector(parameters) except +

        void initFramebuffer(byte_t *frame)
        void simulate(const event *events, int num_events, detection *results, 
                      cid_t *indices)

