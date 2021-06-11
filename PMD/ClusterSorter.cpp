
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
        // auto i = _priority.begin();
        // while (i != _priority.end() && _cluster_buffer[*i].is_tracking) ++i;
        // // mark the cluster as being tracked
        // _cluster_buffer[*i].track();
        // // return cid of the newly tracked cluster
        // return *i;
        size_t i = 0;
        while(i < NO_CID && _cluster_buffer[_priority[i]].is_tracking) ++i;
        _cluster_buffer[_priority[i]].track();
        return _priority[i];
    }
    void ClusterSorter::recalculatePriority() {
        ClusterBuffer &cb = _cluster_buffer;
        std::sort(_priority.begin(), _priority.end(), [&cb](cid_t a, cid_t b) {
            return cb[a].weight > cb[b].weight;
        });
    }
};