
#ifndef _EVENT_HANDLER_H
#define _EVENT_HANDLER_H

#include "types.h"
namespace PMD {
    class PersistentMotionDetector;
    class EventBuffer;
    class ClusterBuffer;
    struct parameters;

    class EventHandler {
        // time cost of processing an event
        uint_t _us_per_event;
        // when the handler will be ready for another event
        ts_t _next_idle_time;
        // how often the handler will flush the input buffer
        uint_t _buffer_flush_period;
        // when the buffer was last flushed
        ts_t _last_buffer_flush;

        // PMD references
        PersistentMotionDetector &_pmd;
        EventBuffer &_event_buffer;
        ClusterBuffer &_cluster_buffer;

        // partition index of this handler
        point _place;
        // area for which this handler if responsible
        rect _domain;

        // thresholds
        ts_t _tf, _tc;
        // min correlated events to allow event through filter
        uint_t _n;
        // maximum size to allow events to cluster
        uint_t _max_cluster_size;

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
    
    protected:
        void flushEventBuffer(ts_t t);
    };
};

#endif