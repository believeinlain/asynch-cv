
#include "ClusterAnalyzer.h"

#include "PersistentMotionDetector.h"
#include "ClusterSorter.h"

namespace PMD {
    ClusterAnalyzer::ClusterAnalyzer(
        ClusterSorter &sorter, 
        ClusterBuffer &cluster_buffer,
        parameters param
    ) : 
        _sorter(sorter), _cluster_buffer(cluster_buffer),
        _param(param) {
    }
    ClusterAnalyzer::~ClusterAnalyzer() {
    }

    detection ClusterAnalyzer::updateDetection() {
        // stop tracking clusters that were cleared by the buffer
        if (_cid != NO_CID && !_cluster_buffer[_cid].is_tracking)
            _cid = NO_CID;

        // get next cluster
        if (_cid == NO_CID) {
            _cid = _sorter.trackNextCluster();
            // reset detection to defaults
            _status = detection();
        }
        // if we have a valid cluster now
        if (_cid != NO_CID) {
            _status.is_positive = true;
            // set the centroid
            point p = _cluster_buffer[_cid].centroid();
            _status.x = p.x;
            _status.y = p.y;
            // set the color
            color c = _sorter.getColor(_cid);
            _status.r = c.r;
            _status.g = c.g;
            _status.b = c.b;
        }
        return _status;
    }
};