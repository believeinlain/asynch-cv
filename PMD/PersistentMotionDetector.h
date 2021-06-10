
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "Partition.h"
#include "EventHandler.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {

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
        std::vector<detection> _results;

    public:
        PersistentMotionDetector(xy_t width, xy_t height, parameters param);
        ~PersistentMotionDetector();

        void initFramebuffer(byte_t *frame);
        void processEvents(const event *events, uint_t num_events, detection *results);

    protected:
        void drawEvent(event e, cid_t cid);
    };
};

#endif
