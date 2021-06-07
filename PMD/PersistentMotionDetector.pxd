
cdef extern from 'types.h' namespace 'PMD':
    ctypedef unsigned short xy_t
    ctypedef int p_t
    ctypedef unsigned long long ts_t

    cdef packed struct event:
        xy_t x
        xy_t y
        p_t p
        ts_t t
        
    ctypedef unsigned char byte_t

    cdef packed struct color:
        byte_t r, g, b

    cdef packed struct point:
        xy_t x, y

cdef extern from 'PersistentMotionDetector.h' namespace 'PMD':
    cdef packed struct parameters:
        int x_div, y_div
        int us_per_event
        int event_buffer_depth
        int tf, tc, n
    
    cdef cppclass PersistentMotionDetector:
        PersistentMotionDetector(int, int, parameters) except +

        void init_framebuffer(byte_t *frame)
        void process_events(const event *events, int num_events)

