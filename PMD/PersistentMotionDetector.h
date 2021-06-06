
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "Partition.h"
#include "InputQueue.h"
#include "EventHandler.h"

namespace PMD {

    struct parameters {
        xy_t x_div = 8;
        xy_t y_div = 8;
        uint_t input_queue_depth = 64;
        uint_t events_per_ms = 0;
    };

    class PersistentMotionDetector {
        friend class EventHandler;
        
        xy_t width, height;

        parameters param;
        uint_t num_parts;

        Partition *partition;
        InputQueue **input_queues;
        EventHandler **event_handlers;

        byte_t *framebuffer;

    public:
        PersistentMotionDetector(xy_t width, xy_t height, parameters param);
        ~PersistentMotionDetector();

        void init_framebuffer(byte_t *frame);

        void input_events(const event *events, uint_t num_events);

        void process_until(timestamp_t time_us);

    protected:
        void draw_event(const event &e);
    };
};

#endif
