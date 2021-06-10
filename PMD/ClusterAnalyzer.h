
#ifndef _CLUSTER_ANALYZER_H
#define _CLUSTER_ANALYZER_H

#include "types.h"

namespace PMD {

    class ClusterPrioritizer;

    class ClusterAnalyzer {

        ClusterPrioritizer &_prioritizer;

        cid_t _tracking = NO_CID;

    public:
        ClusterAnalyzer(ClusterPrioritizer &prioritizer, parameters param);
        ~ClusterAnalyzer();
    };
};

#endif