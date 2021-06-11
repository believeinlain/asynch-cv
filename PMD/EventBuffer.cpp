
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {

    size_t EventBuffer::buffer_queue::depth = 0;

    EventBuffer::EventBuffer(size_t width, size_t height, size_t depth, ClusterBuffer &cluster_buffer) :
        _width(width), _height(height), _depth(depth),
        _cluster_buffer(cluster_buffer)
    {
        // set depth to allocate event buffer
        buffer_queue::depth = depth;

        // allocate buffer memory
        _buffer = new array_2d<buffer_queue>(width, height);
    }
    EventBuffer::~EventBuffer() {
        // deallocate buffer memory
        delete _buffer;
    }

    std::map<cid_t, ushort_t> EventBuffer::checkVicinity(const rect &domain,
        event e, ts_t tf, ts_t tc, ushort_t &num_adjacent) 
    {
        auto adjacent = std::map<cid_t, ushort_t>();

        // clip vicinity to buffer bounds
        size_t x_start = (e.x > 0) ? e.x-1U : 0;
        size_t y_start = (e.y > 0) ? e.y-1U : 0;
        // end values are not inclusive
        size_t x_end = ((e.x+2U) > _width) ? _width : e.x+2U;
        size_t y_end = ((e.y+2U) > _height) ? _height : e.y+2U;

#if USE_THREADS
        // -- lock buffers for access
        _buffer_access.lock();
#endif
        // init count to 0
        num_adjacent = 0;
        for (size_t x = x_start; x < x_end; ++x) {
            for (size_t y = y_start; y < y_end; ++y) {
                for (size_t z = 0; z < _depth; ++z) {
                    auto ts = _buffer->at(x, y)[z].t;
                    auto cid = _buffer->at(x, y)[z].cid;
                    // add to count if within filter threshold
                    if (ts > e.t-tf) num_adjacent++;
                    // add to adjacent clusters if within cluster threshold
                    if ((cid != NO_CID) && (ts > e.t-tc)) adjacent[cid]++;
                }
            }
        }
#if USE_THREADS
        // -- release buffer lock
        _buffer_access.unlock();
#endif

        // return the results
        return adjacent;
    }

    void EventBuffer::flushDomain(ts_t th, rect domain) {
        for (size_t x = domain.tl.x; x < domain.br.x; ++x) {
            for (size_t y = domain.tl.y; y < domain.br.y; ++y) {
                for (size_t z = 0; z < _depth; ++z) {
                    auto ts = _buffer->at(x, y)[z].t;
                    auto cid = _buffer->at(x, y)[z].cid;
                    // if any assigned events are too old, unassign them
                    if ((cid != NO_CID) && (ts < th)) {
#if USE_THREADS
                        // -- lock buffers for access
                        _buffer_access.lock();
#endif
                        // remove expired events from cluster buffer
                        _cluster_buffer[cid].remove(x, y);
                        // and unassign them
                        _buffer->at(x, y)[z].cid = NO_CID;
#if USE_THREADS
                        // -- release buffer lock
                        _buffer_access.unlock();
#endif
                    }
                }
            }
        }
    }

    // add event to buffer, return cid of displaced event
    void EventBuffer::addEvent(event e, cid_t cid) {
#if USE_THREADS
        // -- lock buffers for access
        _buffer_access.lock();
#endif
        // add new event to event buffer
        buffer_entry displaced = _buffer->at(e.x, e.y).push(cid, e.t);

        // add new event to cluster buffer
        if (cid != NO_CID)
            _cluster_buffer[cid].add(e.x, e.y);
        
        // remove displaced event from cluster buffer
        if (displaced.cid != NO_CID) 
            _cluster_buffer[displaced.cid].remove(e.x, e.y);
        
#if USE_THREADS
        // -- release buffer lock
        _buffer_access.unlock();
#endif
    }
};