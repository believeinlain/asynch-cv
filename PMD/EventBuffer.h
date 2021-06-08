
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

    typedef std::map<cid_t, uint_t> cluster_map;
    typedef std::vector<buffered_event> buffered_event_vector;

    class EventBuffer {
        uint_t width;
        uint_t height;
        uint_t depth;
        uint_t size;
        uint_t slice_size;

        ts_t *ts_buffer;
        cid_t *cid_buffer;
        uint_t *top;

    public:
        EventBuffer(uint_t width, uint_t height, uint_t depth);
        ~EventBuffer();

        // return number of adjacent events within tf
        // vector of adjacent cids within tc -> out_adjacent
        uint_t check_vicinity(const event &e, const ts_t &tf, const ts_t &tc, cluster_map &out_adjacent);

        // flush expired events and return those removed
        void flush_domain(ts_t t, const rect &domain, buffered_event_vector &out_removed);
        
        // add event to buffer, return cid of displaced event
        cid_t add_event(const event &e, cid_t cid=UNASSIGNED_CLUSTER);

        // get the cid of the cluster at (x, y) on top
        cid_t get_cid_at(xy_t x, xy_t y);

    };
};

#endif