
#include "ClusterAnalyzer.h"

#include "PersistentMotionDetector.h"
#include "ClusterSorter.h"

#include <iostream>

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
        // if we currently have a cluster
        if (_cid != NO_CID) {
            // check is cluster is empty and untrack if so
            if (_cluster_buffer[_cid].isEmpty())
                _cluster_buffer[_cid]._is_tracking = false;

            // stop tracking if cluster is no longer marked as tracked
            if (!_cluster_buffer[_cid]._is_tracking)
                _cid = NO_CID;
        }
        
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
                _samples.emplace(t, _cluster_buffer[_cid].centroid_f());
    }

    detection ClusterAnalyzer::updateDetection() {
        // always update cid
        _status.cid = _cid;

        // if we have a valid cluster
        if (_cid != NO_CID) {
            // update detection results
            _status.is_active = true;
            // set the centroid
            point p = _cluster_buffer[_cid].centroid();
            _status.x = p.x;
            _status.y = p.y;
            // set the color
            color c = _sorter.getColor(_cid);
            _status.r = c.r;
            _status.g = c.g;
            _status.b = c.b;

            // quit if we don't have enough samples
            if (_samples.size() < 2) return _status;

            // get the time of the most recent sample
            ts_t t = _samples.rbegin()->first;
            ts_t threshold;

            // find the sample at the beginning of the long sample interval
            threshold = t-_p.long_duration;
            if (threshold > t) threshold = 0; // overflow check
            auto long_start = _samples.lower_bound(threshold);
            // erase samples that are too old
            _samples.erase(_samples.begin(), long_start);

            // quit if we don't have enough samples
            if (_samples.size() < 2) return _status;

            // subtract the oldest sample from the most recent
            point_f long_disp = _samples.rbegin()->second - _samples.begin()->second;
            // double long_dt = double(_samples.rbegin()->first - _samples.begin()->first);
            double long_dt = double(_p.long_duration);

            _status.long_v_x = float(long_disp.x*1000000.0/long_dt);
            _status.long_v_y = float(long_disp.y*1000000.0/long_dt);

            // find the sample at the beginning of the short sample interval
            threshold = t-_p.short_duration;
            if (threshold > t) threshold = 0; // overflow check
            auto short_start = _samples.lower_bound(threshold);

            // if we don't and samples in the short interval, quit
            if (short_start == _samples.end()) return _status;

            // calculate the short interval time and displacement
            point_f short_disp = _samples.rbegin()->second - short_start->second;
            // double short_dt = double(_samples.rbegin()->first - short_start->first);
            double short_dt = double(_p.short_duration);

            _status.short_v_x = float(short_disp.x*1000000.0/short_dt);
            _status.short_v_y = float(short_disp.y*1000000.0/short_dt);

            double diff_x = _status.long_v_x - _status.short_v_x;
            double diff_y = _status.long_v_y - _status.short_v_y;

            double diff_radius = sqrt(pow(diff_x, 2) + pow(diff_y, 2));
            double long_radius_sq = pow(_status.long_v_x, 2) + pow(_status.long_v_y, 2);

            _status.ratio = sqrt(long_radius_sq)/(diff_radius+0.0001);

            if (_status.ratio > _p.ratio_threshold)
                _status.stability += int(_status.ratio - _p.ratio_threshold);
            else
                _status.stability += int((_status.ratio - _p.ratio_threshold)*0.1);
        }
        return _status;
    }
};