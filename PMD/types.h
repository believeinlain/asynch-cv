
typedef unsigned short xy_t;
typedef signed char polarity_t;
typedef unsigned long long timestamp_t;
typedef unsigned char color_t;

typedef signed int xy_sum_t;
typedef float xy_float_t;
typedef unsigned int cluster_weight_t;

struct point_t {
    xy_t x, y;
};
    
struct event_t {
    xy_t x, y;
    polarity_t p;
    timestamp_t t;
};