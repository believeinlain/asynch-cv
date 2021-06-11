
#ifndef _CLUSTER_ANALYZER_H
#define _CLUSTER_ANALYZER_H

#include "types.h"

namespace PMD {

    class ClusterSorter;
    class ClusterBuffer;

    class ClusterAnalyzer {
        // PMD refernences
        ClusterSorter &_sorter;
        ClusterBuffer &_cluster_buffer;

        // execution parameters
        parameters _param;

        // cluster that we're currently tracking
        cid_t _cid = NO_CID;

        detection _status{};

    public:
        ClusterAnalyzer(
            ClusterSorter &sorter, 
            ClusterBuffer &cluster_buffer,
            parameters param
        );
        ~ClusterAnalyzer();

        detection updateDetection();
    };
};

#endif