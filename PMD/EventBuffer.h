
#ifndef _EVENT_BUFFER_H
#define _EVENT_BUFFER_H

#include "types.h"

#include <map>
#include <mutex>

namespace PMD {

    class ClusterBuffer;

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
        buffer_entry operator[](point p) const {
            auto top_xy = p.x + _width*p.y;
            auto buffer_xy = _depth*(top_xy);
            return _buffer[buffer_xy + _top[top_xy]];
        }

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