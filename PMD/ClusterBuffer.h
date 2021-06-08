
#ifndef _CLUSTER_BUFFER_H
#define _CLUSTER_BUFFER_H

#include "types.h"

#include <random>
#include <map>

namespace PMD {

    struct cluster {
        cluster(ts_t birth=0) : birth(birth), weight(0),
            x_sum(0), y_sum(0) {}
        ts_t birth;
        uint_t weight;
        uint_t x_sum;
        uint_t y_sum;
    };

    typedef std::map<uint_t, cid_t> sorted_clusters;

    class ClusterBuffer {
        // allocate an array up to but not including NO_CID
        cluster _buffer[NO_CID];
        // rng to assign new cluster ids
        std::mt19937 _rand_gen;
        std::uniform_int_distribution<cid_t> _rand;

    public:
        ClusterBuffer() : _rand_gen(0), _rand(0, NO_CID-1) {}
        ~ClusterBuffer() {}
        // access as an array
        cluster operator[](cid_t cid) const {
            if (cid == NO_CID) return cluster();
            else return _buffer[cid];
        }

        cid_t createNewCluster(ts_t t);
        void addEventToCluster(event e, cid_t cid);
        void removeEventFromCluster(xy_t x, xy_t y, cid_t cid);

        sorted_clusters sort_by_weight();
    };
};

#endif