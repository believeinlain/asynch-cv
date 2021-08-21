
#ifndef _CLUSTER_ANALYZER_H
#define _CLUSTER_ANALYZER_H

#include "types.h"
#include <map>

namespace PMD {

    class ClusterSorter;
    class ClusterBuffer;

    class ClusterAnalyzer {
        // PMD references
        ClusterSorter &_sorter;
        ClusterBuffer &_cluster_buffer;

        // execution parameters
        parameters _p;

        // cluster that we're currently tracking
        cid_t _cid = NO_CID;

        // final detection results
        detection _status;

        // collection of samples
        std::map<ts_t, point_f> _samples;

    public:
        ClusterAnalyzer(
            ClusterSorter &sorter, 
            ClusterBuffer &cluster_buffer,
            parameters p
        );
        ~ClusterAnalyzer();

        void reassignCluster();
        void sampleCluster(ts_t t);
        detection updateDetection();
    };
};

#endif