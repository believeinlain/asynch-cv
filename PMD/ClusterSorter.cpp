
#include "ClusterSorter.h"

#include "ClusterBuffer.h"

#include <algorithm>

namespace PMD {
    ClusterSorter::ClusterSorter(ClusterBuffer &cluster_buffer, parameters param) :
        _cluster_buffer(cluster_buffer)
    {
        // initialize priority array
        for (cid_t cid=0; cid<NO_CID; ++cid)
            _priority[cid] = cid;

        // generate evenly spaced random colors for each cluster
        const double PI = 3.14159265358979311600;
        for (cid_t i=0; i<NO_CID; ++i)
            _colors[i] = color( (float)
                fmod(double(i)*PI*10.0, 360.0), 1.0);
    }

    cid_t ClusterSorter::trackNextCluster() {
        // go through the sorted priority array and assign the first untracked cluster
        size_t i = 0;
        cid_t target = NO_CID;
        for (size_t i = 0; i < NO_CID; ++i) {
            target = _priority[i];
            if (!_cluster_buffer[target].is_tracking && _cluster_buffer[target].weight > 0) 
                break;
        }
        _cluster_buffer[target].track();
        return target;
    }
    void ClusterSorter::recalculatePriority() {
        ClusterBuffer &cb = _cluster_buffer;
        std::sort(_priority.begin(), _priority.end(), [&cb](cid_t a, cid_t b) {
            return cb[a].weight > cb[b].weight;
        });
    }
};