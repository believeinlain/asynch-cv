
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "Partition.h"
#include "InputQueue.h"

namespace PMD {

    struct parameters {
        xy_t x_div = 8;
        xy_t y_div = 8;
        int input_queue_depth = 64;
    };

    class PersistentMotionDetector {
        xy_t width, height;

        parameters param;
        int num_partitions;

        Partition *partition;
        array_2d<InputQueue*> input_queues;

    public:
        PersistentMotionDetector(xy_t width, xy_t height, parameters param);
        ~PersistentMotionDetector();

        void update_frame(array_2d<color> &start_frame, event *events, int num_events);
    };
};

#endif
