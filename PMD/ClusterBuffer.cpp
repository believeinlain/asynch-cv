
#include "ClusterBuffer.h"

namespace PMD {

    void Cluster::createAt(ts_t birth) {
        _birth = birth;
        _weight = 0;
        _x_sum = 0;
        _y_sum = 0;
        _is_centroid_updated = false;
        _centroid = point();
        _is_tracking = false;
    }

    void Cluster::add(xy_t x, xy_t y) {
        ++_weight;
        _x_sum += x;
        _y_sum += y;
        // centroid will need updating
        _is_centroid_updated = false;
    }

    void Cluster::remove(xy_t x, xy_t y) {
        --_weight;
        _x_sum -= x;
        _y_sum -= y;
        // centroid will need updating
        _is_centroid_updated = false;
        // cannot track an empty cluster
        if (_weight == 0) _is_tracking = false;
    }

    bool Cluster::isInRange(xy_t x, xy_t y, uint_t range) {
        point c = centroid();
        return (uint_t(abs(x-c.x) + abs(y-c.y)) < range);
    }
    point Cluster::centroid() {
        // if we need to, and *can* calculate the centroid, do so
        // otherwise just go with the last saved one
        if (!_is_centroid_updated && (_weight > 0)) {
            _centroid = point(_x_sum/_weight, _y_sum/_weight);
            _is_centroid_updated = true;
        }
        return _centroid;
    }

    cid_t ClusterBuffer::createNewCluster(ts_t t) {
        cid_t cid;
        do { // pick a random unoccupied cid
            cid = _rand(_rand_gen);
            // keep trying until we get an unused one
        } while (_buffer[cid].weight > 0);
        
        // set the new cluster's birth time to t
        // and reset all other struct data
        _buffer[cid].createAt(t);

        // return the new cid
        return cid;
    }
};