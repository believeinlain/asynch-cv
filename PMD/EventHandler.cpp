
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
        // catch up processing to the last event time
        this->process_until(events[num_events-1].t);
    }

    void EventHandler::process_event(const event &e) {
        // if we're ready for another event
        if (e.t > this->next_idle_time) {
            // catch up processing
            this->process_until(e.t);
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
                    // maybe parameterize this?

                    // find the cluster with the most adjacent events to this one
                    // auto nearest = adjacent.begin();
                    // for (auto i = next(nearest); i != adjacent.end(); i++)
                    //     if (i->second > nearest->second) nearest = i;
                    // assigned = nearest->first;
                    
                    // find the cluster with the most events total
                    // assigned = adjacent.begin()->first;
                    // for (auto i = next(adjacent.begin()); i != adjacent.end(); i++)
                    //     if ( (this->cluster_buffer->get_cluster(i->first).weight 
                    //         > this->cluster_buffer->get_cluster(assigned).weight) )
                    //         assigned = i->first;

                    // find the cluster with the earliest birth time
                    assigned = adjacent.begin()->first;
                    for (auto i = next(adjacent.begin()); i != adjacent.end(); i++)
                        if ( (this->cluster_buffer->get_cluster(i->first).birth 
                            < this->cluster_buffer->get_cluster(assigned).birth) )
                            assigned = i->first;
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

    void EventHandler::process_until(ts_t t) {
        // check if it's time to flush the buffer
        if (t > this->last_buffer_flush+this->buffer_flush_period)
            this->flush_event_buffer(t);
    }

    void EventHandler::flush_event_buffer(ts_t t) {
        this->last_buffer_flush = t;

        buffered_event_vector removed;
        this->event_buffer->flush_domain(t-this->tc, this->domain, removed);

        for (auto i = removed.begin(); i != removed.end(); i++)
            this->cluster_buffer->remove_event_from_cluster(i->x, i->y, i->cid);
    }
};