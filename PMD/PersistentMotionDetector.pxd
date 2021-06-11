
from libcpp cimport bool

cdef extern from 'types.h' namespace 'PMD':
    cdef packed struct parameters:
        int x_div, y_div
        int us_per_event
        int event_buffer_depth
        int tf, tc, n
        int buffer_flush_period
        int max_cluster_size
        int num_analyzers

    cdef packed struct detection:
        int is_positive
        int x, y
        int r, g, b
        int cid

    ctypedef unsigned short xy_t
    ctypedef int p_t
    ctypedef unsigned long long ts_t
    ctypedef unsigned short cid_t

    cdef packed struct event:
        xy_t x, y
        p_t p
        ts_t t
        
    ctypedef unsigned char byte_t

cdef extern from 'PersistentMotionDetector.h' namespace 'PMD':
    cdef cppclass PersistentMotionDetector:
        PersistentMotionDetector(int, int, parameters) except +

        void initFramebuffer(byte_t *frame)
        void processEvents(const event *events, int num_events, detection *results, cid_t *indices)

