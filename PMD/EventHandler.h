
#ifndef _EVENT_HANDLER_H
#define _EVENT_HANDLER_H

#include "types.h"
#include "InputQueue.h"


namespace PMD {
    class PersistentMotionDetector;

    class EventHandler {
        // time cost of processing an event (for simulation/consistency)
        uint_t us_per_event;
        // reference to the corresponding input queue
        InputQueue *input_queue;
        // reference to the overall PMD
        PersistentMotionDetector *pmd;
        // time to limit rate of event processing
        timestamp_t current_time_us;

    public:
        EventHandler(PersistentMotionDetector *pmd, InputQueue *input_queue, uint_t us_per_event);
        ~EventHandler();

        void process_until(timestamp_t time_us);
    };
};

#endif