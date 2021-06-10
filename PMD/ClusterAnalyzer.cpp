
#include "ClusterAnalyzer.h"

#include "PersistentMotionDetector.h"

namespace PMD {
    ClusterAnalyzer::ClusterAnalyzer(ClusterPrioritizer &prioritizer, parameters param) : 
        _prioritizer(prioritizer) {
    }
    ClusterAnalyzer::~ClusterAnalyzer() {
    }
};