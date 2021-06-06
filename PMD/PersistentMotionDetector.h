
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
        uint_t event_handler_us_per_event = 0;
        uint_t input_queue_expiration_us = 0;
    };

    struct detection {
        bool is_positive;
        point position;
        point velocity;
        float confidence;
    };

    enum event_result {
        EVENT_REJECTED,
        EVENT_FILTERED,
        EVENT_CLUSTERED
    };

    struct processed_event {
        point position;
        event_result result;
        color c;
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

        uint_t input_events_until(timestamp_t time_us, const event *events, uint_t num_events, uint_t start_at);

        void process_until(timestamp_t time_us);

    protected:
        void event_callback(const event &e, bool is_filtered=false, cluster_id_t cluster=UNASSIGNED_CLUSTER);
    };
};

#endif
