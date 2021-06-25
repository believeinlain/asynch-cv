
#include "ClusterSorter.h"

#include "ClusterBuffer.h"

#include <algorithm>

#include <iostream>

namespace PMD {
    ClusterSorter::ClusterSorter(ClusterBuffer &cluster_buffer, parameters param) :
        _cluster_buffer(cluster_buffer)
    {
        constexpr double PI = 3.14159265358979311600;

        // initialize arrays
        for (cid_t cid=0; cid<NO_CID; ++cid) {
            _birth_order[cid] = cid;
            _weight_order[cid] = cid;
            // generate evenly spaced random colors for each cluster
            _colors[cid] = color( fmod(double(cid)*PI*10.0, 360.0), 1.0);
        }
    }

    cid_t ClusterSorter::trackNextCluster() {
        // go through the sorted priority array and assign the first untracked cluster
        cid_t target = NO_CID;

        for (cid_t i=0; i<NO_CID; ++i) {
            // find the first available target by either weight or birth order
            target = _weight_order[i];
            if (!_cluster_buffer[target]._is_tracking) 
                break;
            
            // target = _birth_order[i];
            // if (!_cluster_buffer[target].is_tracking && !_cluster_buffer[target].isEmpty()) 
            //     break;
        }
        
        _cluster_buffer[target].track();

        return target;
    }
    void ClusterSorter::recalculatePriority() {
        ClusterBuffer &cb = _cluster_buffer;
        std::sort(_weight_order.begin(), _weight_order.end(), [&cb](cid_t a, cid_t b) {
            return cb[a]._weight > cb[b]._weight;
        });
        std::sort(_birth_order.begin(), _birth_order.end(), [&cb](cid_t a, cid_t b) {
            // put empty clusters last
            if (cb[a].isEmpty()) return false;
            else if (cb[b].isEmpty()) return true;
            // put zero-birth clusters last
            else if (cb[a]._birth == 0) return false;
            else if (cb[b]._birth == 0) return true;
            // sort clusters with nonzero birth and weight
            else return cb[a]._birth < cb[b]._birth;
        });
        // std::cout << "sorted clusters, weight order ";
        // for (int i=0; i<16; ++i) std::cout << cb[_weight_order[i]]._weight << ' ';
        // std::cout << std::endl;
        // std::cout << "sorted clusters, birth order ";
        // for (int i=0; i<16; ++i) std::cout << _birth_order[i] << ' ';
        // std::cout << std::endl;
    }
};