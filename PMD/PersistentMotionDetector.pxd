
from libcpp cimport bool

cdef extern from 'types.h' namespace 'PMD':
    cdef packed struct parameters:
        int width, height
        int x_div, y_div
        int us_per_event
        int event_buffer_depth
        int tf, tc, n
        int buffer_flush_period
        int max_cluster_size
        int num_analyzers
        int sample_period
        int sample_collection_duration
        int velocity_threshold

    cdef packed struct detection:
        int is_positive
        int x, y
        int r, g, b
        int cid
        float v_x, v_y
        int path_length
        int stability
        float consistency

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
        PersistentMotionDetector(parameters) except +

        void initFramebuffer(byte_t *frame)
        void simulate(const event *events, int num_events, detection *results, cid_t *indices)

