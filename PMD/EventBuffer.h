
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

        struct buffer_queue {
            // set this before instantiating
            static size_t depth;

            buffer_queue() 
                { _queue = new buffer_entry[depth]{}; }
            ~buffer_queue() 
                { delete[] _queue; }
            buffer_entry &operator[](size_t z) 
                { return _queue[z]; }
            buffer_entry const &operator[](size_t z) const 
                { return _queue[z]; }
            buffer_entry &top() 
                { return _queue[_top]; }
            buffer_entry const &top() const 
                { return _queue[_top]; }
            buffer_entry push(cid_t cid, ts_t t) {
                _top = (_top + 1) % depth;
                buffer_entry new_entry;
                new_entry.cid = cid;
                new_entry.t = t;
                buffer_entry displaced = _queue[_top];
                _queue[_top] = new_entry;
                return displaced;
            }
        private:
            size_t _top = 0;
            buffer_entry *_queue;
        };

        size_t _width;
        size_t _height;
        size_t _depth;
        
        // pointer so we can delay allocation until we set depth
        array_2d<buffer_queue> *_buffer;
        ClusterBuffer &_cluster_buffer;

#if USE_THREADS
        std::mutex _buffer_access;
#endif

    public:
        EventBuffer(size_t width, size_t height, size_t depth, ClusterBuffer &cluster_buffer);
        ~EventBuffer();

        // accessor can only read the top of the buffer
        const buffer_queue &at(size_t x, size_t y) const {
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