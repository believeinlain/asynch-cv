
# type definitions
ctypedef unsigned char bool

ctypedef unsigned short xy_t
ctypedef signed char polarity_t
ctypedef unsigned long long timestamp_t
ctypedef unsigned char color_t

ctypedef signed int xy_sum_t
ctypedef float xy_float_t
ctypedef unsigned int cluster_weight_t

# structs
cdef packed struct point_t:
    xy_t x, y
    
cdef packed struct event_t:
    xy_t x, y
    polarity_t p
    timestamp_t t