# distutils: language = c++

cdef extern from 'types.h':
    ctypedef unsigned short xy_t
    ctypedef signed char polarity_t
    ctypedef unsigned long long timestamp_t

    cdef packed struct color:
        unsigned char r, g, b

    cdef packed struct point:
        xy_t x, y
        
    # cdef packed struct event:
    #     xy_t x, y
    #     polarity_t p
    #     timestamp_t t

    cdef cppclass array_2d[T]:
        array_2d(int width, int height)
        array_2d(int width, int height, T *data)
        void put(int i, int j, T val)
        T get(int i, int j)

# for some reason including this in extern breaks things
cdef packed struct event:
    xy_t x, y
    polarity_t p
    timestamp_t t

cdef extern from 'Partition.h' namespace 'PMD':
    cdef cppclass Partition:
        pass

cdef extern from 'PersistentMotionDetector.h' namespace 'PMD':
    cdef packed struct parameters:
        xy_t x_div, y_div
        int input_queue_depth
    
    cdef cppclass PersistentMotionDetector:
        PersistentMotionDetector(int, int, parameters) except +

        xy_t width, height

        parameters param
        int num_partitions

        Partition *partition
        array_2d input_queues

        void update_frame(array_2d frame, event *events, int num_events)
