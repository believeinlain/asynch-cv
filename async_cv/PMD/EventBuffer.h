
#ifndef _EVENT_BUFFER_H
#define _EVENT_BUFFER_H

#include "types.h"

#include "options.h"

#include <map>
#if USE_THREADS
#include <mutex>
#endif

namespace PMD {

    class ClusterBuffer;

    class EventBuffer {
        struct buffer_entry {
            cid_t cid = NO_CID;
            ts_t t = 0;
        };

        size_t _width;
        size_t _height;
        size_t _depth;
        
        // pointer so we can delay allocation until we set depth
        buffer_3d<buffer_entry> *_buffer;
        ClusterBuffer &_cluster_buffer;

#if USE_THREADS
        std::mutex _buffer_access;
#endif

    public:
        EventBuffer(size_t width, size_t height, size_t depth, ClusterBuffer &cluster_buffer);
        ~EventBuffer();

        // accessor can only read the top of the buffer
        const buffer_entry &at(size_t x, size_t y) const {
            return _buffer->at(x, y);
        }

        // return number of adjacent events within tf
        // vector of adjacent cids within tc -> out_adjacent
        std::map<cid_t, ushort_t> checkVicinity(const rect &d,
            event e, ts_t tf, ts_t tc, ushort_t &num_adjacent);

        // flush expired events and remove from cluster buffer
        void flushDomain(ts_t th, rect domain);
        
        // add event to buffer, remove displaced event from cluster buffer
        void addEvent(event e, cid_t cid=NO_CID);

    private:
        buffer_entry &at(size_t x, size_t y, size_t z);
    };
};

#endif