
#ifndef _EVENT_BUFFER_H
#define _EVENT_BUFFER_H

#include "types.h"

#include <map>
#include <mutex>

namespace PMD {

    class ClusterBuffer;

    struct buffered_event {
        buffered_event(xy_t x, xy_t y, cid_t cid) :
            x(x), y(y), cid(cid) {}
        xy_t x, y;
        cid_t cid; 
    };

    class EventBuffer {
        struct buffer_entry {
            cid_t cid = NO_CID;
            ts_t t = 0;
        };

        xy_t _width;
        xy_t _height;
        ushort_t _depth;
        
        ClusterBuffer &_cluster_buffer;

        buffer_entry *_buffer;
        ushort_t *_top;

        std::mutex buffer_access;

    public:
        EventBuffer(xy_t width, xy_t height, ushort_t depth, ClusterBuffer &cluster_buffer);
        ~EventBuffer();

        // accessor can only read the top of the buffer
        buffer_entry operator[](point p) const;

        // return number of adjacent events within tf
        // vector of adjacent cids within tc -> out_adjacent
        std::map<cid_t, ushort_t> checkVicinity(
            event e, ts_t tf, ts_t tc, ushort_t &num_adjacent);

        // flush expired events and remove from cluster buffer
        void flushDomain(ts_t th, rect domain);
        
        // add event to buffer, remove displaced event from cluster buffer
        void addEvent(event e, cid_t cid=NO_CID);
    };
};

#endif