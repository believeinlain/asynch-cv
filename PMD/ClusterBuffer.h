
#ifndef _CLUSTER_BUFFER_H
#define _CLUSTER_BUFFER_H

#include "types.h"

#include <random>
#include <iostream>
#include <array>

namespace PMD {

    class Cluster {
        friend class EventBuffer;

        ts_t _birth = 0;
        int _weight = 0;
        int _x_sum = 0;
        int _y_sum = 0;
        bool _is_centroid_updated = false;
        point _centroid{};
        bool _is_tracking = false;

    public:
        // getter references
        const ts_t &birth = _birth;
        const int &weight = _weight;
        const bool &is_tracking = _is_tracking;

        // reset all values and set new birth time
        void createAt(ts_t birth);
        // begin tracking this cluster
        void track() { _is_tracking = true; }

        bool isInRange(int x, int y, int range);
        const point &centroid();

    protected:
        // these are only meant to be accessed by the event buffer
        // can otherwise lead to issues with threading
        void add(int x, int y);
        void remove(int x, int y);
    };

    class ClusterBuffer {
        // allocate an array up to but not including NO_CID
        std::array<Cluster, NO_CID> _buffer;
        // rng to assign new cluster ids
        std::mt19937 _rand_gen;
        std::uniform_int_distribution<cid_t> _rand;

    public:
        ClusterBuffer() : _rand_gen(0), _rand(0, NO_CID-1), _buffer() {}

        // access buffer as an array
        Cluster &operator[](cid_t cid) {
            // throw error for invalid index
            if (cid == NO_CID) 
                throw std::out_of_range("Attempted to index Cluster with invalid cid of NO_CID.");
            else return _buffer[cid];
        }

        // find an unused cid and initialize it in the buffer
        cid_t createNewCluster(ts_t t);
    };
};

#endif