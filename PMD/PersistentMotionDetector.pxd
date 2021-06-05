# distutils: language = c++

cdef extern from 'types.h':
    ctypedef unsigned short xy_t
    ctypedef signed char polarity_t
    ctypedef unsigned long long timestamp_t
    ctypedef unsigned char byte_t

    cdef packed struct color:
        byte_t r, g, b

    cdef packed struct point:
        xy_t x, y

    # cdef enum event_result:
    #     EVENT_REJECTED
    #     EVENT_FILTERED
    #     EVENT_CLUSTERED

    # cdef packed struct processed_event:
    #     point position
    #     event_result result
    #     color c

    # cdef packed struct detection:
    #     char is_positive
    #     point position
    #     point velocity
    #     float confidence

    cdef packed struct event:
        xy_t x
        xy_t y
        polarity_t p
        timestamp_t t

cdef extern from 'PersistentMotionDetector.h' namespace 'PMD':
    cdef packed struct parameters:
        xy_t x_div, y_div
        int input_queue_depth
    
    cdef cppclass PersistentMotionDetector:
        PersistentMotionDetector(int, int, parameters) except +

        void process_events(byte_t *frame, event *events, int num_events)
