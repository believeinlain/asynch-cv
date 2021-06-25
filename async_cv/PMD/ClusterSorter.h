
#ifndef _CLUSTER_SORTER_H
#define _CLUSTER_SORTER_H

#include "types.h"

#include <array>

namespace PMD {
    class ClusterBuffer;

    class ClusterSorter {
        
        // PMD references
        ClusterBuffer &_cluster_buffer;

        // cids in different orders
        std::array<cid_t, NO_CID> _weight_order;
        std::array<cid_t, NO_CID> _birth_order;

        // keep track of cluster colors
        std::array<color, NO_CID> _colors;

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