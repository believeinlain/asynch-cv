
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "Partition.h"
#include "EventHandler.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {

    struct parameters {
        ushort_t x_div = 8;
        ushort_t y_div = 8;
        uint_t us_per_event = 0;
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
        
        xy_t _width, _height;

        parameters _param;
        uint_t _num_parts;

        Partition _partition;
        EventHandler **_event_handlers;
        EventBuffer _event_buffer;
        ClusterBuffer _cluster_buffer;

        byte_t *_framebuffer;
        color _cluster_colors[NO_CID];

    public:
        PersistentMotionDetector(
            xy_t width, xy_t height, parameters param);
        ~PersistentMotionDetector();

        void initFramebuffer(byte_t *frame);
        void processEvents(const event *events, uint_t num_events);

    protected:
        void eventCallback(event e, cid_t cid);
    };
};

#endif
