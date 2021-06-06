
#include "EventHandler.h"

#include "PersistentMotionDetector.h"
#include "InputQueue.h"
#include "EventBuffer.h"

namespace PMD {
    EventHandler::EventHandler(
            PersistentMotionDetector *pmd, 
            InputQueue *input_queue, 
            EventBuffer *event_buffer,
            const parameters &param
    ) :
        pmd(pmd),
        input_queue(input_queue), 
        event_buffer(event_buffer),
        us_per_event(param.event_handler_us_per_event),
        input_queue_expiration_us(param.input_queue_expiration_us),
        tf(param.tf),
        tc(param.tc),
        n(param.n),
        current_time_us(0)
    {}

    void EventHandler::process_until(ts_t time_us) {
        // if the queue is empty, just return
        const event *front = this->input_queue->peek();
        if (front == nullptr) return;

        event e;
        // while we still have time and there are still events to process
        while ((this->current_time_us <= time_us) && this->input_queue->pop(e)) {
            // if event is expired, skip it
            if (this->input_queue_expiration_us > 0)
                if (e.t < this->current_time_us-this->input_queue_expiration_us) 
                    continue;
            
            // actually process the event
            cid_vector adjacent = cid_vector();
            uint_t count = this->event_buffer->check_vicinity(e, this->tf, this->tc, adjacent);
            cid_t assigned = UNASSIGNED_CLUSTER;
            bool is_filtered = (count < this->n);
            this->pmd->event_callback(e, is_filtered, assigned);
            this->event_buffer->add_event(e, assigned);

            // current time must at least be the time this event fired
            if (e.t > this->current_time_us) this->current_time_us = e.t;
            // plus the time it took to process
            this->current_time_us += this->us_per_event;
        }
        // make sure we update the time appropriately
        if (time_us > this->current_time_us) this->current_time_us = time_us;
    }
};