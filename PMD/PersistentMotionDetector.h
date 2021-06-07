
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "Partition.h"
#include "EventHandler.h"
#include "EventBuffer.h"

namespace PMD {

    struct parameters {
        xy_t x_div = 8;
        xy_t y_div = 8;
        uint_t us_per_event = 0;
        uint_t event_buffer_depth = 4;
        uint_t tf = 200000;
        uint_t tc = 200000;
        uint_t n = 5;
    };
/* 
    struct detection {
        bool is_positive;
        point position;
        point velocity;
        float confidence;
    };
 */
    class PersistentMotionDetector {
        friend class EventHandler;
        
        xy_t width, height;

        parameters param;
        uint_t num_parts;

        Partition *partition;
        EventHandler **event_handlers;
        EventBuffer *event_buffer;

        byte_t *framebuffer;

    public:
        PersistentMotionDetector(xy_t width, xy_t height, parameters param);
        ~PersistentMotionDetector();

        void init_framebuffer(byte_t *frame);

        void process_events(const event *events, uint_t num_events);

    protected:
        void event_callback(const event &e, bool is_filtered=false, cid_t cluster=UNASSIGNED_CLUSTER);
    };
};

#endif
