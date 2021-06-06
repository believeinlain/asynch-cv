
#ifndef _EVENT_BUFFER_H
#define _EVENT_BUFFER_H

#include "types.h"

#include <vector>

namespace PMD {

    typedef std::vector<cid_t> cid_vector;

    class EventBuffer {
        event *buffer;

    public:
        EventBuffer(uint_t width, uint_t height, uint_t depth);
        ~EventBuffer();

        int check_vicinity(const event &e, const ts_t &tf, const ts_t &tc, cid_vector &out_adjacent);
    };
};

#endif