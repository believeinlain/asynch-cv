
#ifndef _EVENT_HANDLER_H
#define _EVENT_HANDLER_H

#include "types.h"
#include "InputQueue.h"


namespace PMD {
    class PersistentMotionDetector;

    class EventHandler {
        // events the handler will process for each ms of operation
        // 0 for unlimited
        uint_t events_per_ms;
        // reference to the corresponding input queue
        InputQueue *input_queue;
        // reference to the overall PMD
        PersistentMotionDetector *pmd;

    public:
        EventHandler(PersistentMotionDetector *pmd, InputQueue *input_queue, uint_t events_per_ms);
        ~EventHandler();

        void process_until(timestamp_t time_us);
    };
};

#endif