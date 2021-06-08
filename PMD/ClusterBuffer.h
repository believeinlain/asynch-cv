
#ifndef _CLUSTER_BUFFER_H
#define _CLUSTER_BUFFER_H

#include "types.h"

#include <random>

namespace PMD {

    struct cluster {
        cluster(ts_t birth=0) : birth(birth), weight(0),
            x_sum(0), y_sum(0), is_tracking(false) {}
        ts_t birth;
        uint_t weight;
        uint_t x_sum;
        uint_t y_sum;
        bool is_tracking;
    };

    class ClusterBuffer {
        // allocate an array where up to but not including
        // the UNASSIGNED value can be assigned to a cluster
        cluster buffer[UNASSIGNED_CLUSTER];
        // rng to assign new cluster ids
        std::mt19937 rand_gen;
        std::uniform_int_distribution<cid_t> rand;

    public:
        ClusterBuffer() : rand_gen(0), rand(0, UNASSIGNED_CLUSTER-1) {}
        ~ClusterBuffer() {}

        cid_t create_new_cluster(ts_t t);
        void add_event_to_cluster(const event &e, cid_t cid);
        void remove_event_from_cluster(xy_t x, xy_t y, cid_t cid);
    };
};

#endif