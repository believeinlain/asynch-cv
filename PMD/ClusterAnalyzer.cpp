
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

            // quit if we don't have enough samples
            if (_samples.size() < 2) return _status;

            // get the time of the most recent sample
            ts_t t = _samples.rbegin()->first;

            // find the sample at the beginning of the long sample interval
            auto long_start = _samples.lower_bound(t-_p.long_duration);
            // erase samples that are too old
            _samples.erase(_samples.begin(), long_start);

            // quit if we don't have enough samples
            if (_samples.size() < 2) return _status;

            // subtract the oldest sample from the most recent
            point_f long_disp = _samples.rbegin()->second - _samples.begin()->second;
            double long_dt = double(_p.long_duration);

            _status.long_v_x = float(long_disp.x*1000000.0/long_dt);
            _status.long_v_y = float(long_disp.y*1000000.0/long_dt);

            // find the sample at the beginning of the short sample interval
            auto short_start = _samples.lower_bound(t-_p.short_duration);

            // if we don't and samples in the short interval, quit
            if (short_start == _samples.end()) return _status;

            // calculate the short interval time and displacement
            point_f short_disp = _samples.rbegin()->second - short_start->second;
            double short_dt = double(_p.short_duration);

            _status.short_v_x = float(short_disp.x*1000000.0/short_dt);
            _status.short_v_y = float(short_disp.y*1000000.0/short_dt);

            double diff_x = _status.long_v_x - _status.short_v_x;
            double diff_y = _status.long_v_y - _status.short_v_y;

            double diff_radius = sqrt(pow(diff_x, 2) + pow(diff_y, 2));
            double long_radius = sqrt(pow(_status.long_v_x, 2) + pow(_status.long_v_y, 2));

            double ratio = (long_radius > 0) ? diff_radius/long_radius : 0;
            double times_over = (ratio > 0) ? long_radius/ratio : 0;

            // if (times_over > _p.velocity_threshold)
            _status.stability += times_over - _p.velocity_threshold;

            // calculate the velocity (in pixels per second)
            // point_f disp = _samples.back().second - _samples.front().second;
            // double dt = double(_samples.back().first - _samples.front().first);
            // dt = double(_p.sample_collection_duration);
            // // estimate the path length integral using samples
            // double path = 0;
            // auto a = _samples.begin();
            // auto b = a;
            // ++b;
            // while (b != _samples.end()) {
            //     path += sqrt(pow(b->second.x - a->second.x, 2) + pow(b->second.y - a->second.y, 2));
            //     ++a; ++b;
            // }
            // // scale results by time elapsed
            // if (dt > 0) {
            //     double v_x = (disp.x*1000000) / dt;
            //     double v_y = (disp.y*1000000) / dt;
            //     double speed = sqrt(pow(v_x, 2) + pow(v_y, 2));
            //     _status.stability += int(speed) - _p.velocity_threshold;
            //     _status.v_x = (float)v_x;
            //     _status.v_y = (float)v_y;
            // }
            // if (path > 0) {
            //     _status.consistency = sqrt(pow(disp.x, 2) + pow(disp.y, 2))/path;
            // }
        }
        return _status;
    }
};