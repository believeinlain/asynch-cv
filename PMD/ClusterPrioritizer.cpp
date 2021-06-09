
#include "ClusterPrioritizer.h"

#include "ClusterBuffer.h"

#include <algorithm>

using namespace std;

namespace PMD {
    ClusterPrioritizer::ClusterPrioritizer(ClusterBuffer &cluster_buffer) :
        _cluster_buffer(cluster_buffer)
    {
        cid_t cid = 0;
        for (auto &i : _cluster_priority) cid++;
    }

    cid_t trackNextCluster() {

    }
    void recalculatePriority() {

    }
};