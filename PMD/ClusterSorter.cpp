
#include "ClusterSorter.h"

#include "ClusterBuffer.h"

#include <algorithm>

namespace PMD {
    ClusterSorter::ClusterSorter(ClusterBuffer &cluster_buffer, parameters param) :
        _cluster_buffer(cluster_buffer)
    {
        constexpr double PI = 3.14159265358979311600;

        // initialize arrays
        for (cid_t cid=0; cid<NO_CID; ++cid){
            _birth_order[cid] = cid;
            _weight_order[cid] = cid;
            // generate evenly spaced random colors for each cluster
            _colors[cid] = color( fmod(double(cid)*PI*10.0, 360.0), 1.0);
        }
    }

    cid_t ClusterSorter::trackNextCluster() {
        // go through the sorted priority array and assign the first untracked cluster
        cid_t i = 0;
        cid_t target = NO_CID;
        bool seeking_target = true;
        do {
            // find the first available target by either weight or birth order
            target = _weight_order[i];
            if (!_cluster_buffer[target].is_tracking && _cluster_buffer[target].weight > 0) 
                seeking_target = false;
            else 
            target = _birth_order[i];
            if (!_cluster_buffer[target].is_tracking && _cluster_buffer[target].weight > 0) 
                seeking_target = false;
            ++i;
        } while ((i < NO_CID) && seeking_target);
        _cluster_buffer[target].track();

        return target;
    }
    void ClusterSorter::recalculatePriority() {
        ClusterBuffer &cb = _cluster_buffer;
        std::sort(_weight_order.begin(), _weight_order.end(), [&cb](cid_t a, cid_t b) {
            return cb[a].weight > cb[b].weight;
        });
        std::sort(_birth_order.begin(), _birth_order.end(), [&cb](cid_t a, cid_t b) {
            if (cb[a].weight <= 0) return false;
            else if (cb[b].weight <= 0) return true;
            else if (cb[a].birth == 0) return false;
            else if (cb[b].birth == 0) return false;
            else return cb[a].birth < cb[b].birth;
        });
    }
};