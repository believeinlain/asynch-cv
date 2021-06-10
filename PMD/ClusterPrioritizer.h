
#ifndef _CLUSTER_PRIORITIZER_H
#define _CLUSTER_PRIORITIZER_H

#include "types.h"

#include <array>

namespace PMD {
    class ClusterBuffer;

    class ClusterPrioritizer {
        
        // PMD references
        ClusterBuffer &_cluster_buffer;

        // cids in order of priority
        std::array<cid_t, NO_CID> _priority;

    public:
        ClusterPrioritizer(ClusterBuffer &cluster_buffer, parameters param);

        cid_t trackNextCluster();
        void recalculatePriority();
    };
};

#endif