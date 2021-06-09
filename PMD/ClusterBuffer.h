
#ifndef _CLUSTER_BUFFER_H
#define _CLUSTER_BUFFER_H

#include "types.h"

#include <random>
#include <array>
#include <iostream>

namespace PMD {

    struct cluster {
        ts_t birth = 0;
        uint_t weight = 0;
        uint_t x_sum = 0;
        uint_t y_sum = 0;
        bool is_tracking = false;
        point centroid() {
            // should not happen, but this will prevent a crash on divide by zero
            if (weight==0) { 
                std::cout<<"\nError: Cannot find centroid of empty cluster."<<std::endl;
                return point(0,0);
            }
            else return point(x_sum/weight, y_sum/weight);
        }
    };

    class ClusterBuffer {
        friend class EventBuffer;

        // allocate an array up to but not including NO_CID
        cluster _buffer[NO_CID];
        // rng to assign new cluster ids
        std::mt19937 _rand_gen;
        std::uniform_int_distribution<cid_t> _rand;

    public:
        ClusterBuffer() : _rand_gen(0), _rand(0, NO_CID-1), _buffer() {}
        ~ClusterBuffer() {}
        // access as an array
        cluster operator[](cid_t cid) const {
            if (cid == NO_CID) return cluster();
            else return _buffer[cid];
        }

        cid_t createNewCluster(ts_t t);

    protected:
        // these are only meant to be accesed by the event buffer
        void addEventToCluster(event e, cid_t cid);
        void removeEventFromCluster(xy_t x, xy_t y, cid_t cid);

        // std::array<cid_t, NO_CID> sortByWeight();
    };
};

#endif