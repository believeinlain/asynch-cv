
#ifndef _EVENT_HANDLER_H
#define _EVENT_HANDLER_H

#include "types.h"

namespace PMD {
    class PersistentMotionDetector;
    class EventBuffer;
    struct parameters;

    class EventHandler {
        // time cost of processing an event
        uint_t us_per_event;
        // when the handler will be ready for another event
        ts_t next_idle_time;

        // PMD reference pointers
        PersistentMotionDetector *pmd;
        EventBuffer *event_buffer;

        // thresholds
        uint_t tf, tc;
        // min correlated events to allow event through filter
        uint_t n;

    public:
        EventHandler(PersistentMotionDetector *pmd, EventBuffer *event_buffer, const parameters &param);
        ~EventHandler() {}

        void process_event(const event &e);
    };
};

#endif