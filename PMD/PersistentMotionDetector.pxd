
cdef extern from 'types.h' namespace 'PMD':
    cdef packed struct event:
        unsigned short x
        unsigned short y
        int p
        unsigned long long t
        
    ctypedef unsigned char byte_t

    cdef packed struct color:
        byte_t r, g, b

cdef extern from 'PersistentMotionDetector.h' namespace 'PMD':
    cdef packed struct parameters:
        int x_div, y_div
        int us_per_event
        int event_buffer_depth
        int tf, tc, n
        int buffer_flush_period
    
    cdef cppclass PersistentMotionDetector:
        PersistentMotionDetector(int, int, parameters) except +

        void init_framebuffer(byte_t *frame)
        void process_events(const event *events, int num_events)

