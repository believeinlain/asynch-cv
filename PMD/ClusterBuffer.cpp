
#include "ClusterBuffer.h"

namespace PMD {
    cid_t ClusterBuffer::create_new_cluster(ts_t t) {
        cid_t cid;
        do { // pick a random unoccupied cid
            cid = this->rand(this->rand_gen);
        } while (this->buffer[cid].weight > 0);
        
        // set the new cluster's birth time to t
        // and reset all other struct data
        this->buffer[cid] = cluster(t);

        // return the new cid
        return cid;
    }
    void ClusterBuffer::add_event_to_cluster(const event &e, cid_t cid) {
        this->buffer[cid].weight++;
        this->buffer[cid].x_sum += e.x;
        this->buffer[cid].y_sum += e.y;
    }
    void ClusterBuffer::remove_event_from_cluster(xy_t x, xy_t y, cid_t cid) {
        this->buffer[cid].weight--;
        this->buffer[cid].x_sum -= x;
        this->buffer[cid].y_sum -= y;
    }
};