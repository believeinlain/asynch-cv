
#include "ClusterPrioritizer.h"

#include "ClusterBuffer.h"

#include <algorithm>

namespace PMD {
    ClusterPrioritizer::ClusterPrioritizer(ClusterBuffer &cluster_buffer) :
        _cluster_buffer(cluster_buffer)
    {
        // initialize priority array
        for (cid_t cid=0; cid<NO_CID; ++cid)
            _priority[cid] = cid;
    }

    cid_t ClusterPrioritizer::trackNextCluster() {
        // go through the sorted priority array and assign the first untracked cluster
        auto i = _priority.begin();
        while (i != _priority.end() && _cluster_buffer[*i].is_tracking) ++i;
        // mark the cluster as being tracked
        _cluster_buffer.trackCluster(*i);
        // return cid of the newly tracked cluster
        return *i;
    }
    void ClusterPrioritizer::recalculatePriority() {
        // just sort by weight for now
        std::sort(_priority.begin(), _priority.end(), [this](cid_t a, cid_t b) {
            return _cluster_buffer[a].weight > _cluster_buffer[b].weight;
        });
    }
};