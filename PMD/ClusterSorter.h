
#ifndef _CLUSTER_SORTER_H
#define _CLUSTER_SORTER_H

#include "types.h"

#include <array>

namespace PMD {
    class ClusterBuffer;

    class ClusterSorter {
        
        // PMD references
        ClusterBuffer &_cluster_buffer;

        // cids in order of priority
        std::array<cid_t, NO_CID> _priority;

        // keep track of cluster colors here
        color _colors[NO_CID];

    public:
        ClusterSorter(ClusterBuffer &cluster_buffer, parameters param);

        inline color getColor(cid_t cid) {
            return (cid==NO_CID) ? color(120) : _colors[cid];
        }

        cid_t trackNextCluster();
        void recalculatePriority();
    };
};

#endif