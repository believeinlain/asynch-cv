
#ifndef _TYPES_H
#define _TYPES_H

#include <limits>

namespace PMD {
    // types carefully chosen to fit 4-byte alignment
    // this is important because of how it interfaces with python
    typedef unsigned short xy_t; // 2 bytes
    typedef int polarity_t; // should be 4 bytes
    typedef unsigned long long timestamp_t; // 8 bytes

    struct event {
        xy_t x; // 2 bytes
        xy_t y; // 2 bytes
        polarity_t p; // 4 bytes
        timestamp_t t; // 8 bytes
    }; // total 16 bytes per event - only 13 of which are really needed

    // define convenient shorthand for single byte variables
    // this is used to pass frame-data to/from python, so it's important
    typedef unsigned char byte_t;
    // just a general unsigned integer since I use them a lot
    typedef unsigned int uint_t;

    struct color {
        color(byte_t r, byte_t g, byte_t b) :
            r(r), g(g), b(b) {}
        color(byte_t v) :
            r(v), g(v), b(v) {}
        color() : r(0), g(0), b(0) {}
        byte_t r, g, b;
        // allow indexing as an array
        byte_t &operator[](uint_t index) {
            if (index == 1) return g;
            else if (index == 2) return b;
            else return r;
        }
    };

    struct point {
        xy_t x, y;
    };

    struct rect {
        point tl, br;
    };

    typedef unsigned int cluster_id_t;
    const cluster_id_t UNASSIGNED_CLUSTER = std::numeric_limits<cluster_id_t>::max();
    const unsigned long MAX_CLUSTERS = UNASSIGNED_CLUSTER + 1;
};

#endif