
#include "ClusterBuffer.h"

namespace PMD {
    cid_t ClusterBuffer::createNewCluster(ts_t t) {
        cid_t cid;
        do { // pick a random unoccupied cid
            cid = _rand(_rand_gen);
        } while (_buffer[cid].weight > 0);
        
        // set the new cluster's birth time to t
        // and reset all other struct data
        _buffer[cid] = cluster();
        _buffer[cid].birth = t;

        // return the new cid
        return cid;
    }
    void ClusterBuffer::addEventToCluster(event e, cid_t cid) {
        _buffer[cid].weight++;
        _buffer[cid].x_sum += e.x;
        _buffer[cid].y_sum += e.y;
    }
    void ClusterBuffer::removeEventFromCluster(xy_t x, xy_t y, cid_t cid) {
        _buffer[cid].weight--;
        _buffer[cid].x_sum -= x;
        _buffer[cid].y_sum -= y;
        // cannot track an empty cluster
        if (_buffer[cid].weight==0) _buffer[cid].is_tracking = false;
    }
};