
#include "EventHandler.h"

#include "PersistentMotionDetector.h"
#include "EventBuffer.h"

namespace PMD {
    EventHandler::EventHandler(
        PersistentMotionDetector *pmd, EventBuffer *event_buffer, point place, rect domain, const parameters &param) :
            pmd(pmd), event_buffer(event_buffer), place(place), domain(domain), 
            us_per_event(param.us_per_event), tf(param.tf), tc(param.tc), n(param.n), next_idle_time(0)
    {}

    void EventHandler::process_event_buffer(const event *events, uint_t num_events) {
        // iterate through the sequence of events
        for (uint_t i=0; i<num_events; i++) {
            const event &e = events[i];
            // handle the event
            if (this->domain.contains(e.x, e.y)) {
                this->process_event(e);
            }
        }
    }

    inline void EventHandler::process_event(const event &e) {
        // if we're ready for another event
        if (e.t > this->next_idle_time) {
            // process the event
            cid_vector adjacent = cid_vector();
            uint_t count = this->event_buffer->check_vicinity(e, this->tf, this->tc, adjacent);
            cid_t assigned = UNASSIGNED_CLUSTER;
            bool is_filtered = (count < this->n);
            this->pmd->event_callback(e, is_filtered, assigned);
            this->event_buffer->add_event(e, assigned);

            // compute when we'll be ready for another event
            this->next_idle_time = e.t + this->us_per_event;
        }
    }
};