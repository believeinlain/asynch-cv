
#include "EventHandler.h"

#include "PersistentMotionDetector.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {
    EventHandler::EventHandler(
        PersistentMotionDetector &pmd, 
        EventBuffer &event_buffer, 
        ClusterBuffer &cluster_buffer,
        point place, rect domain, 
        parameters param
    ) :
        _pmd(pmd), 
        _event_buffer(event_buffer), 
        _cluster_buffer(cluster_buffer), 
        _place(place), _domain(domain), 
        _us_per_event(param.us_per_event), 
        _tf(param.tf), _tc(param.tc), _n(param.n), 
        _buffer_flush_period(param.buffer_flush_period),
        _next_idle_time(0), _last_buffer_flush(0)
    {}

    void EventHandler::processEventBuffer(
        const event *events, uint_t num_events) 
    {
        // iterate through the sequence of events
        for (uint_t i=0; i<num_events; ++i)
            if (_domain.contains(events[i].x, events[i].y))
                processEvent(events[i]);
        
        // catch up processing to the last event time
        processUntil(events[num_events-1].t);
    }

    void EventHandler::processEvent(event e) {
        // if we're ready for another event
        if (e.t > _next_idle_time) {
            // catch up processing
            processUntil(e.t);
            // process the event
            ushort_t count = 0;
            auto adj = _event_buffer.checkVicinity(e, _tf, _tc, count);
            
            cid_t assigned = NO_CID;
            // cluster only if passed the correlational filter
            if (count >= _n) {
                // if no adjacent clusters, make a new one
                if (adj.empty()) 
                    assigned = _cluster_buffer.createNewCluster(e.t);
                // just one adjacent cluster, assign to that
                else if (adj.size() == 1) 
                    assigned = adj.begin()->first;
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
                    assigned = adj.begin()->first;
                    for (auto i = next(adj.begin()); i != adj.end(); ++i)
                        if ( (_cluster_buffer[i->first].birth 
                            < _cluster_buffer[assigned].birth) )
                            assigned = i->first;
                }
                
                // add to cluster buffer
                _cluster_buffer.addEventToCluster(e, assigned);
            }

            // callback to draw the event on the frame buffer
            _pmd.eventCallback(e, assigned);
            
            // add the event to the event buffer
            cid_t displaced = _event_buffer.addEvent(e, assigned);

            // remove displaced event from cluster buffer if applicable
            if (displaced != NO_CID)
                _cluster_buffer.removeEventFromCluster(e.x, e.y, displaced);

            // compute when we'll be ready for another event
            _next_idle_time = e.t + _us_per_event;
        }
    }

    void EventHandler::processUntil(ts_t t) {
        // check if it's time to flush the buffer
        if (t > _last_buffer_flush+_buffer_flush_period)
            flushEventBuffer(t);
    }

    void EventHandler::flushEventBuffer(ts_t t) {
        _last_buffer_flush = t;

        auto rem = _event_buffer.flushDomain(t-_tc, _domain);

        for (auto i = rem.begin(); i != rem.end(); ++i)
            _cluster_buffer.removeEventFromCluster(i->x, i->y, i->cid);
    }
};