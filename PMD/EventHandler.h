
#ifndef _EVENT_HANDLER_H
#define _EVENT_HANDLER_H

#include "types.h"

namespace PMD {
    
    class PersistentMotionDetector;
    class EventBuffer;
    class ClusterBuffer;

    class EventHandler {

        // PMD references
        PersistentMotionDetector &_pmd;
        EventBuffer &_event_buffer;
        ClusterBuffer &_cluster_buffer;

        // execution parameters
        parameters _param;

        // partition index of this handler
        point _place;
        // area for which this handler is responsible
        rect _domain;

        // when the handler will be ready for another event
        ts_t _next_idle_time = 0;
        // when the buffer was last flushed
        ts_t _last_buffer_flush = 0;

    public:
        EventHandler(
            PersistentMotionDetector &pmd, 
            EventBuffer &event_buffer, 
            ClusterBuffer &cluster_buffer, 
            point place, rect domain, 
            parameters param);
        ~EventHandler() {}

        // process an entire buffer of events
        void processEventBuffer(const event *events, uint_t num_events);
        // process a single event
        void processEvent(event e);
        // catch up processing in case the handler receives no events for a while
        void processUntil(ts_t t);
    };
};

#endif