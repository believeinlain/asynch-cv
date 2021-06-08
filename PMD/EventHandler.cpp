
#include "EventHandler.h"

#include "PersistentMotionDetector.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"

#include <iostream>
using namespace std;
namespace PMD {
    EventHandler::EventHandler(
        PersistentMotionDetector *pmd, 
        EventBuffer *event_buffer, 
        ClusterBuffer *cluster_buffer,
        point place, 
        rect domain, 
        const parameters &param
    ) :
        pmd(pmd), 
        event_buffer(event_buffer), 
        cluster_buffer(cluster_buffer), 
        place(place), 
        domain(domain), 
        us_per_event(param.us_per_event), 
        tf(param.tf), tc(param.tc), n(param.n), 
        next_idle_time(0),
        buffer_flush_period(param.buffer_flush_period),
        last_buffer_flush(0)
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
            cluster_map adjacent = cluster_map();
            uint_t count = this->event_buffer->check_vicinity(e, this->tf, this->tc, adjacent);
            
            cid_t assigned = UNASSIGNED_CLUSTER;

            // cluster only if passed the correlational filter
            if (count >= this->n) {
                // if no adjacent clusters, make a new one
                if (adjacent.empty()) assigned = this->cluster_buffer->create_new_cluster(e.t);
                // just one adjacent cluster, assign to that
                else if (adjacent.size() == 1) assigned = adjacent.begin()->first;
                // otherwise decide what to do
                else {
                    // find the cluster with the most adjacent events to this one
                    auto nearest = adjacent.begin();
                    for (auto i = next(nearest); i != adjacent.end(); i++)
                        if (i->second > nearest->second) nearest = i;

                    assigned = nearest->first;
                }
                
                // add to cluster buffer
                this->cluster_buffer->add_event_to_cluster(e, assigned);
            }

            // callback to draw the event on the frame buffer
            this->pmd->event_callback(e, assigned);
            
            // add the event to the event buffer
            cid_t displaced = this->event_buffer->add_event(e, assigned);

            // remove displaced event from cluster buffer if applicable
            if (displaced != UNASSIGNED_CLUSTER)
                this->cluster_buffer->remove_event_from_cluster(e.x, e.y, displaced);

            // compute when we'll be ready for another event
            this->next_idle_time = e.t + this->us_per_event;
        }
    }

    void flush_event_buffer(ts_t t) {
        
    }
};