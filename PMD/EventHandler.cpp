
#include "EventHandler.h"
#include "PersistentMotionDetector.h"

#include <iostream>

namespace PMD {
    EventHandler::EventHandler(PersistentMotionDetector *pmd, InputQueue *input_queue, uint_t events_per_ms) :
        pmd(pmd), input_queue(input_queue), events_per_ms(events_per_ms)
    {}
    EventHandler::~EventHandler() {}

    void EventHandler::process_until(timestamp_t time_us) {
        // if the queue is empty, just return
        const event *front = this->input_queue->peek();
        if (front == nullptr) return;

        // initialize time to earliest event in queue
        timestamp_t last_time = front->t;
        // calculate the max number of events we can to process
        uint_t event_limit = this->events_per_ms*(time_us - last_time)/1000;
        // no event limit if events_per_ms is set to 0
        bool is_limited = this->events_per_ms > 0;
        // count the events we've processed
        uint_t event_count = 0;

        event e;
        while ((event_count <= event_limit) && (last_time <= time_us) && this->input_queue->pop(e)) {
            this->pmd->draw_event(e);
            last_time = e.t;
            if (is_limited) event_count++;
        }
    }
};