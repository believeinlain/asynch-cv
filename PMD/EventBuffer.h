
#ifndef _EVENT_BUFFER_H
#define _EVENT_BUFFER_H

#include "types.h"

#include <map>
#include <vector>

namespace PMD {

    struct buffered_event {
        buffered_event(xy_t x, xy_t y, cid_t cid) :
            x(x), y(y), cid(cid) {}
        xy_t x, y;
        cid_t cid; 
    };

    typedef std::map<cid_t, ushort_t> cluster_count_map;
    typedef std::vector<buffered_event> buffered_event_vector;

    class EventBuffer {
        struct buffer_entry {
            cid_t cid = NO_CID;
            ts_t t = 0;
        };

        xy_t _width;
        xy_t _height;
        ushort_t _depth;

        buffer_entry *_buffer;
        ushort_t *_top;

    public:
        EventBuffer(xy_t width, xy_t height, ushort_t depth);
        ~EventBuffer();

        // accessor can only read the top of the buffer
        buffer_entry operator[](point p) const;

        // return number of adjacent events within tf
        // vector of adjacent cids within tc -> out_adjacent
        cluster_count_map checkVicinity(
            event e, ts_t tf, ts_t tc, ushort_t &num_adjacent);

        // flush expired events and return those removed
        buffered_event_vector flushDomain(ts_t th, rect domain);
        
        // add event to buffer, return cid of displaced event
        cid_t addEvent(event e, cid_t cid=NO_CID);
    };
};

#endif