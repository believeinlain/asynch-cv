
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "Partition.h"
#include "EventHandler.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {

    struct parameters {
        xy_t x_div = 8;
        xy_t y_div = 8;
        ushort_t us_per_event = 0;
        ushort_t event_buffer_depth = 4;
        ts_t tf = 200000;
        ts_t tc = 200000;
        ushort_t n = 5;
        uint_t buffer_flush_period = 1000;
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
        
        uint_t width, height;

        parameters param;
        uint_t num_parts;

        Partition *partition;
        EventHandler **event_handlers;
        EventBuffer *event_buffer;
        ClusterBuffer *cluster_buffer;

        byte_t *framebuffer;
        color cluster_colors[UNASSIGNED_CLUSTER];

    public:
        PersistentMotionDetector(uint_t width, uint_t height, parameters param);
        ~PersistentMotionDetector();

        void init_framebuffer(byte_t *frame);
        void process_events(const event *events, uint_t num_events);

    protected:
        void event_callback(const event &e, bool is_filtered, cid_t cid);
    };
};

#endif
