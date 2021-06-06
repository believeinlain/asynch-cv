
#include "EventBuffer.h"

namespace PMD {
    EventBuffer::EventBuffer(uint_t width, uint_t height, uint_t depth)  :
        width(width), height(height), depth(depth), size(width*height*depth), slice_size(width*height)
    {
        // allocate buffer memory
        this->ts_buffer = new ts_t[size];
        this->cid_buffer = new cid_t[size];
        this->top = new uint_t[slice_size];

        // initialize values
        for (int i=0; i<size; i++) {
            this->ts_buffer[i] = 0;
            this->cid_buffer[i] = UNASSIGNED_CLUSTER;
        }
        for (int i=0; i<slice_size; i++) 
            this->top[i] = 0;
    }
    EventBuffer::~EventBuffer() {
        delete[] this->ts_buffer;
        delete[] this->cid_buffer;
        delete[] this->top;
    }

    uint_t EventBuffer::check_vicinity(const event &e, const ts_t &tf, const ts_t &tc, cid_vector &out_adjacent) {
        // clip vicinity to buffer bounds
        uint_t x_start = (e.x <= 0) ? 0 : e.x - 1;
        uint_t y_start = (e.y <= 0) ? 0 : e.y - 1;
        uint_t x_end = (e.x >= this->width) ? this->width : e.x + 1;
        uint_t y_end = (e.y >= this->height) ? this->height : e.y + 1;

        // make output vector fit max adjacent clusters
        out_adjacent.reserve((x_end-x_start)*(y_end-y_start)*this->depth*sizeof(cid_t));

        uint_t buffer_xy, index; 
        ts_t ts;
        cid_t cid;
        uint_t count = 0;
        for (uint_t i = x_start; i < x_end; i++) {
            for (uint_t j = y_start; j < y_end; j++) {
                buffer_xy = this->depth*(i + this->width*j);
                // iterate through all depth positions at this xy
                for (index = buffer_xy; index < (buffer_xy+this->depth); index++) {
                    ts = this->ts_buffer[index];
                    cid = this->cid_buffer[index];
                    // add to count if within filter threshold
                    if (ts > e.t-tf) count++;
                    // add to adjacent clusters if within cluster threshold
                    if ((ts > e.t-tc) && (cid != UNASSIGNED_CLUSTER)) out_adjacent.push_back(cid);
                }
            }
        }

        // free unused space in output vector
        out_adjacent.shrink_to_fit();

        // return the results
        return count;
    }

    // add event to buffer, return cid of displaced event
    cid_t EventBuffer::add_event(const event &e, cid_t cid) {
        // compute the xy position in 2d top array
        const uint_t top_xy = e.x + this->width*e.y;
        this->top[top_xy] = (this->top[top_xy] + 1) % this->depth;
        
        // get the new event position in the 3d buffers
        const uint_t index = this->depth*top_xy + this->top[top_xy];

        // determine return value based on displaced event
        cid_t result = UNASSIGNED_CLUSTER;
        if (this->cid_buffer[index] != UNASSIGNED_CLUSTER)
            result = this->cid_buffer[index];
        
        // place the new event in the buffers
        this->ts_buffer[index] = e.t;
        this->cid_buffer[index] = cid;

        return result;
    }
};