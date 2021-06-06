
#include "EventHandler.h"
#include "PersistentMotionDetector.h"

#include <iostream>

namespace PMD {
    EventHandler::EventHandler(PersistentMotionDetector *pmd, InputQueue *input_queue, uint_t us_per_event) :
        current_time_us(0), pmd(pmd), input_queue(input_queue), us_per_event(us_per_event)
    {}
    EventHandler::~EventHandler() {}

    void EventHandler::process_until(timestamp_t time_us) {
        // if the queue is empty, just return
        const event *front = this->input_queue->peek();
        if (front == nullptr) return;

        event e;
        // while we still have time and there are still events to process
        while ((this->current_time_us <= time_us) && this->input_queue->pop(e)) {
            // actually process the event
            this->pmd->draw_event(e);
            // current time must at least be the time this event fired
            if (e.t > this->current_time_us) this->current_time_us = e.t;
            // plus the time it took to process
            this->current_time_us += this->us_per_event;
        }
        // make sure we update the time appropriately
        if (time_us > this->current_time_us) this->current_time_us = time_us;
    }
};