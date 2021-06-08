
#ifndef _EVENT_BUFFER_H
#define _EVENT_BUFFER_H

#include "types.h"

#include <map>

namespace PMD {

    typedef std::map<cid_t, uint_t> cluster_map;

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

        // add event to buffer, return cid of displaced event
        cid_t add_event(const event &e, cid_t cid=UNASSIGNED_CLUSTER);

        // get the cid of the cluster at (x, y) on top
        cid_t get_cid_at(xy_t x, xy_t y);
    };
};

#endif