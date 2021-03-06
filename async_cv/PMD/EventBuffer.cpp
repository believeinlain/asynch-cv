
#include "EventBuffer.h"
#include "ClusterBuffer.h"

namespace PMD {

    EventBuffer::EventBuffer(size_t width, size_t height, size_t depth, ClusterBuffer &cluster_buffer) :
        _width(width), _height(height), _depth(depth),
        _cluster_buffer(cluster_buffer)
    {
        // allocate buffer memory
        _buffer = new buffer_3d<buffer_entry>(width, height, depth);
    }
    EventBuffer::~EventBuffer() {
        // deallocate buffer memory
        delete _buffer;
    }

    std::map<cid_t, ushort_t> EventBuffer::checkVicinity(const rect &d,
        event e, ts_t tf, ts_t tc, ushort_t &num_adjacent) 
    {
        auto adjacent = std::map<cid_t, ushort_t>();

        // clip vicinity to buffer bounds
        size_t x_start = (e.x > 0) ? e.x-1U : 0;
        size_t y_start = (e.y > 0) ? e.y-1U : 0;
        // end values are not inclusive
        size_t x_end = ((e.x+2U) > _width) ? _width : e.x+2U;
        size_t y_end = ((e.y+2U) > _height) ? _height : e.y+2U;

        // init count to 0
        num_adjacent = 0;
        for (size_t x = x_start; x < x_end; ++x) {
            for (size_t y = y_start; y < y_end; ++y) {
                for (size_t z = 0; z < _depth; ++z) {
                    // if we were to lock here if would prevent cluster weights
                    // from going below 0, but that is harmless and preventing it
                    // causes significant slowdown.
                    const auto &p = _buffer->at(x, y, z);
                    // add to count if within filter threshold
                    if (p.t > e.t-tf) num_adjacent++;
                    // add to adjacent clusters if within cluster threshold
                    if ((p.cid != NO_CID) && (p.t > e.t-tc)) adjacent[p.cid]++;
                }

            }
        }

        // return the results
        return adjacent;
    }

    void EventBuffer::flushDomain(ts_t th, rect domain) {
        for (int x = domain.tl.x; x < domain.br.x; ++x) {
            for (int y = domain.tl.y; y < domain.br.y; ++y) {
                for (size_t z = 0; z < _depth; ++z) {
                    auto ts = _buffer->at(x, y, z).t;
                    auto cid = _buffer->at(x, y, z).cid;
                    // if any assigned events are too old, unassign them
                    if ((cid != NO_CID) && (ts < th)) {
#if USE_THREADS
                        // locking here seems to prevent empty clusters from
                        // maintaining positive weight and therefore not
                        // being untracked even with no events
                        // -- lock buffers for access
                        _buffer_access.lock();
#endif
                        // remove expired events from cluster buffer
                        _cluster_buffer[cid].remove(x, y);
                        // and unassign them
                        _buffer->at(x, y, z).cid = NO_CID;
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
        // not sure if we want to lock here
        // locking here seems to limit jittering of near-empty clusters
        // which isn't very important to avoid
        // -- lock buffers for access
        _buffer_access.lock();
#endif
        // add new event to event buffer
        buffer_entry new_entry;
        new_entry.cid = cid;
        new_entry.t = e.t;
        buffer_entry displaced = _buffer->push(e.x, e.y, new_entry);

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