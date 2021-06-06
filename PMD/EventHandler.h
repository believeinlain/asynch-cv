
#ifndef _EVENT_HANDLER_H
#define _EVENT_HANDLER_H

#include "types.h"

namespace PMD {
    class PersistentMotionDetector;
    class InputQueue;
    class EventBuffer;
    struct parameters;

    class EventHandler {
        // time cost of processing an event (for simulation/consistency)
        uint_t us_per_event;
        uint_t input_queue_expiration_us;
        // PMD reference pointers
        PersistentMotionDetector *pmd;
        InputQueue *input_queue;
        EventBuffer *event_buffer;
        // time to limit rate of event processing
        ts_t current_time_us;
        // thresholds
        uint_t tf, tc;
        // min correlated events to allow event through filter
        uint_t n;

    public:
        EventHandler(PersistentMotionDetector *pmd, InputQueue *input_queue, 
            EventBuffer *event_buffer, const parameters &param);
        ~EventHandler() {}

        void process_until(ts_t time_us);
    };
};

#endif