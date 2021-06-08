
#include "EventBuffer.h"

using namespace std;
namespace PMD {
    EventBuffer::EventBuffer(xy_t width, xy_t height, ushort_t depth)  :
        _width(width), _height(height), _depth(depth) 
    {
        uint_t slice_size = width*height;
        uint_t size = slice_size*depth;
        // allocate buffer memory
        _top = new ushort_t[slice_size]();
        _buffer = new buffer_entry[size]();

        // init buffer
        for (uint_t i = 0; i < width; ++i) {
            for (uint_t j = 0; j < height; ++j) {
                // get the xy position in our buffers
                auto buffer_xy = _depth*(i + _width*j);
                // iterate through all depth positions at this xy
                for (auto k = buffer_xy; k < (buffer_xy+_depth); ++k) {
                    _buffer[k].t = 0;
                    _buffer[k].cid = NO_CID;
                }
            }
        }
    }
    EventBuffer::~EventBuffer() 
    {
        // deallocate buffer memory
        delete[] _top;
        delete[] _buffer;
    }

    EventBuffer::buffer_entry EventBuffer::operator[](point p) const {
        auto top_xy = p.x + _width*p.y;
        auto buffer_xy = _depth*(top_xy);
        return _buffer[buffer_xy + _top[top_xy]];
    }

    cluster_count_map EventBuffer::checkVicinity(
        event e, ts_t tf, ts_t tc, ushort_t &num_adjacent) 
    {
        auto adjacent = cluster_count_map();

        // clip vicinity to buffer bounds
        auto x_start = (e.x > 0) ? e.x-1U : 0;
        auto y_start = (e.y > 0) ? e.y-1U : 0;
        // end values are not inclusive
        auto x_end = ((e.x+2U) > _width) ? _width : e.x+2U;
        auto y_end = ((e.y+2U) > _height) ? _height : e.y+2U;

        // init count to 0
        num_adjacent = 0;
        for (auto i = x_start; i < x_end; ++i) {
            for (auto j = y_start; j < y_end; ++j) {
                // get the xy position in our buffers
                auto buffer_xy = _depth*(i + _width*j);
                // iterate through all depth positions at this xy
                for (auto k = buffer_xy; k < (buffer_xy+_depth); ++k) {
                    auto ts = _buffer[k].t;
                    auto cid = _buffer[k].cid;
                    // add to count if within filter threshold
                    if (ts > e.t-tf) num_adjacent++;
                    // add to adjacent clusters if within cluster threshold
                    if ((cid != NO_CID) && (ts > e.t-tc)) adjacent[cid]++;
                }
            }
        }

        // return the results
        return adjacent;
    }

    buffered_event_vector EventBuffer::flushDomain(ts_t th, rect domain) {
        auto removed = buffered_event_vector();

        for (auto i = domain.tl.x; i < domain.br.x; ++i) {
            for (auto j = domain.tl.y; j < domain.br.y; ++j) {
                // get the xy position in our buffers
                auto buffer_xy = _depth*(i + _width*j);
                // iterate through all depth positions at this xy
                for (auto k = buffer_xy; k < (buffer_xy+_depth); ++k) {
                    auto ts = _buffer[k].t;
                    auto cid = _buffer[k].cid;
                    // if any assigned events are too old, unassign them
                    if ((cid != NO_CID) && (ts < th)) {
                        removed.push_back(buffered_event(i, j, cid));
                        _buffer[k].cid = NO_CID;
                    }
                }
            }
        }

        return removed;
    }

    // add event to buffer, return cid of displaced event
    cid_t EventBuffer::addEvent(event e, cid_t cid) {
        // compute the xy position in 2d top array
        auto top_xy = e.x + _width*e.y;
        _top[top_xy] = (_top[top_xy] + 1) % _depth;
        
        // get the new event position in the 3d buffers
        auto k = _depth*top_xy + _top[top_xy];

        // determine return value based on displaced event
        cid_t result = _buffer[k].cid;
        
        // place the new event in the buffers
        _buffer[k].t = e.t;
        _buffer[k].cid = cid;

        return result;
    }
};