
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
        _param(param)
    {}

    void EventHandler::processEventBuffer(
        const event *events, uint_t num_events) 
    {
        // iterate through the sequence of events
        for (uint_t i=0; i<num_events; ++i)
            if (_domain.contains(events[i].x, events[i].y))
                processEvent(events[i]);
        
        // catch up processing to the last event time
        // in case no events went to this event handler
        processUntil(events[num_events-1].t);
    }

    void EventHandler::processEvent(event e) {
        // if we're ready for another event
        if (e.t > _next_idle_time) {
            // catch up processing
            processUntil(e.t);
            // process the event
            ushort_t count = 0;
            auto adj = _event_buffer.checkVicinity(e, _param.tf, _param.tc, count);
            
            cid_t assigned = NO_CID;
            // cluster only if passed the correlational filter
            if (count >= _param.n) {
                bool in_range;
                do {
                    // if no adjacent clusters, make a new one
                    if (adj.empty()) {
                        assigned = _cluster_buffer.createNewCluster(e.t);
                        in_range = true;
                    } else {
                        // just one adjacent cluster, assign to that
                        if (adj.size() == 1)
                            assigned = adj.begin()->first;
                        // otherwise assign to the best one
                        else {
                            // find the cluster with the earliest birth time
                            assigned = adj.begin()->first;
                            for (auto i = next(adj.begin()); i != adj.end(); ++i)
                                if ( (_cluster_buffer[i->first].birth 
                                    < _cluster_buffer[assigned].birth) )
                                    assigned = i->first;
                        }
                        in_range = _cluster_buffer[assigned].isInRange(e.x, e.y, _param.max_cluster_size);
                        // if the centroid of the assigned cluster is too far, don't join it
                        if (!in_range) adj.erase(assigned);
                    }
                    // keep looking if we can't find one close enough
                } while (!in_range);
            }

            // callback to draw the event on the frame buffer
            _pmd.drawEvent(e, assigned);
            
            // add the event to the event buffer
            _event_buffer.addEvent(e, assigned);

            // compute when we'll be ready for another event
            _next_idle_time = e.t + _param.us_per_event;
        }
    }

    void EventHandler::processUntil(ts_t t) {
        // check if it's time to flush the buffer
        if (t > _last_buffer_flush+_param.buffer_flush_period) {
            // flush the buffer if it's time
            _last_buffer_flush = t;
            _event_buffer.flushDomain(t-_param.tc, _domain);
        }
    }
};