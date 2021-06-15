
#include "ClusterAnalyzer.h"

#include "PersistentMotionDetector.h"
#include "ClusterSorter.h"

namespace PMD {
    ClusterAnalyzer::ClusterAnalyzer(
        ClusterSorter &sorter, 
        ClusterBuffer &cluster_buffer,
        parameters p
    ) : 
        _sorter(sorter), _cluster_buffer(cluster_buffer),
        _p(p), _status() {
    }
    ClusterAnalyzer::~ClusterAnalyzer() {
    }

    void ClusterAnalyzer::reassignCluster() {
        // stop tracking clusters that were cleared by the buffer
        if (_cid != NO_CID && !_cluster_buffer[_cid].is_tracking)
            _cid = NO_CID;

        // get next cluster
        if (_cid == NO_CID) {
            _cid = _sorter.trackNextCluster();
            // clear tracked samples
            _samples.clear();
            // reset detection to defaults
            _status = detection();
        }
    }
    void ClusterAnalyzer::sampleCluster(ts_t t) {
        // if we have a valid cluster
        if (_cid != NO_CID)
            // record a new sample
            if (!_cluster_buffer[_cid].isEmpty())
                _samples.emplace_back(t, _cluster_buffer[_cid].centroid_f());
    }

    detection ClusterAnalyzer::updateDetection() {
        // if we have a valid cluster
        if (_cid != NO_CID) {
            // update detection results
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
            // remove samples that are too old
            if (_samples.size() > 1) {
                ts_t t = _samples.back().first;
                _samples.remove_if([this, t](std::pair<ts_t, point_f> s) {
                    return s.first+_p.sample_collection_duration < t; 
                });
            }
            if (_samples.size() > 1) {
                // calculate the velocity (in pixels per second)
                point_f disp = _samples.back().second - _samples.front().second;
                double dt = double(_samples.back().first - _samples.front().first);
                dt = double(_p.sample_collection_duration);
                // estimate the path length integral using samples
                double path = 0;
                auto a = _samples.begin();
                auto b = a;
                ++b;
                while (b != _samples.end()) {
                    path += sqrt(pow(b->second.x - a->second.x, 2) + pow(b->second.y - a->second.y, 2));
                    ++a; ++b;
                }
                // scale results by time elapsed
                if (dt > 0) {
                    double v_x = (disp.x*1000000) / dt;
                    double v_y = (disp.y*1000000) / dt;
                    double speed = sqrt(pow(v_x, 2) + pow(v_y, 2));
                    _status.stability += int(speed) - _p.velocity_threshold;
                    _status.v_x = (float)v_x;
                    _status.v_y = (float)v_y;
                }
                if (path > 0) {
                    _status.consistency = sqrt(pow(disp.x, 2) + pow(disp.y, 2))/path;
                }
            }
        }
        // always update cid
        _status.cid = _cid;
        return _status;
    }
};