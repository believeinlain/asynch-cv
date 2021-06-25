
#include "EventHandler.h"

#include "PersistentMotionDetector.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {
    EventHandler::EventHandler(
        PersistentMotionDetector &pmd, 
        EventBuffer &event_buffer, 
        ClusterBuffer &cluster_buffer,
        point place,
        parameters p
    ) :
        _pmd(pmd), 
        _event_buffer(event_buffer), 
        _cluster_buffer(cluster_buffer), 
        _place(place),
        _p(p),
        _domain(
            (p.width/p.x_div)*(place.x),
            (p.height/p.y_div)*(place.y),
            (p.width/p.x_div)*(place.x+1),
            (p.height/p.y_div)*(place.y+1)
        )
    {}

    void EventHandler::processEventBuffer(
        const event *events, size_t num_events) 
    {
        // catch up processing to the last event time
        // in case no events went to this event handler
        processUntil(events[num_events-1].t);

        // iterate through the sequence of events
        for (size_t i=0; i<num_events; ++i)
            if (_domain.contains(events[i].x, events[i].y))
                processEvent(events[i]);
    }

    void EventHandler::processEvent(event e) {
        // if we're ready for another event
        if (e.t > _next_idle_time) {
            // catch up processing
            processUntil(e.t);

            // temporal filter
            if (e.t < _event_buffer.at(e.x, e.y).t+_p.temporal_filter) return;

            // process the event
            ushort_t count = 0;
            auto adj = _event_buffer.checkVicinity(_domain,
                e, _p.tf, _p.tc, count);
            
            cid_t assigned = NO_CID;
            // cluster only if passed the correlational filter
            if (count >= _p.n) {
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
                                if ( (_cluster_buffer[i->first]._birth 
                                    < _cluster_buffer[assigned]._birth) )
                                    assigned = i->first;
                        }
                        in_range = _cluster_buffer[assigned].isInRange(e.x, e.y, _p.max_cluster_size);
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
            _next_idle_time = e.t + _p.us_per_event;
        }
    }

    inline void EventHandler::processUntil(ts_t t) {
        // check if it's time to flush the buffer
        if (t > _last_buffer_flush+_p.buffer_flush_period) {
            // flush the buffer if it's time
            _last_buffer_flush = t;
            _event_buffer.flushDomain(t-_p.tc, _domain);
        }
    }
};