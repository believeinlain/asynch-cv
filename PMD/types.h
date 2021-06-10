
#ifndef _TYPES_H
#define _TYPES_H

#include <cstdint>
#include <math.h>

namespace PMD {

    // integer types to make interfacing easier,
    // since speed and compactness are not super important here
    struct detection {
        int is_positive = 0;
        int x = 0, y = 0;
        int r = 0, g = 0, b = 0;
    };

    // types used to interface with python bindings
    typedef unsigned short xy_t;
    typedef int p_t;
    typedef unsigned long long ts_t;

    // types carefully chosen to fit 4-byte alignment
    // this is important because of how it interfaces with python
    struct event {
        xy_t x; // 2 bytes
        xy_t y; // 2 bytes
        p_t p; // 4 bytes
        ts_t t; // 8 bytes
    }; // total 16 bytes per event

    // this is used to access the framebuffer, so it's important to be a single byte
    typedef unsigned char byte_t;
    
    // general unsigned integert shorthands
    typedef unsigned int uint_t;
    typedef unsigned int ushort_t;

    // execution parameters
    struct parameters {
        ushort_t x_div = 8;
        ushort_t y_div = 8;
        uint_t us_per_event = 0;
        ushort_t event_buffer_depth = 4;
        ts_t tf = 200000;
        ts_t tc = 200000;
        ushort_t n = 5;
        uint_t buffer_flush_period = 1000;
        uint_t max_cluster_size = 50;
        uint_t num_analyzers = 8;
    };

    struct color {
        // rgb, int from 0 tp 255
        color(byte_t r, byte_t g, byte_t b) :
            r(r), g(g), b(b) {}
        // hue - float from 0.0 to 360.0, vibrance - float from 0 to 1
        color(float h, float v) {
            byte_t c = byte_t( v*255.0 );
            byte_t x = byte_t( v*255.0*(1.0 - fabs(fmod(h/60.0, 2.0) - 1.0)) );
            if (h < 60.0) { r = c; g = x; b = 0; }
            else if (h < 120.0) { r = x; g = c; b = 0; }
            else if (h < 180.0) { r = 0; g = c; b = x; }
            else if (h < 240.0) { r = 0; g = x; b = c; }
            else if (h < 300.0) { r = x; g = 0; b = c; }
            else { r = c; g = 0; b = x; }
        }
        // intensity, int from 0 to 255
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
        point(xy_t x, xy_t y) : x(x), y(y) {}
        point() : x(0), y(0) {}
        xy_t x, y;
    };

    struct rect {
        rect(xy_t tlx, xy_t tly, xy_t brx, xy_t bry) : 
            tl(tlx, tly), br(brx, bry) {}
        rect() : tl(), br() {}
        point tl, br;
        inline bool contains(xy_t x, xy_t y) {
            return (tl.x <= x) 
                && (tl.y <= y) 
                && (x < br.x) 
                && (y < br.y);
        }
    };

    // should be exactly 16 bits since this affects cluster buffer size
    typedef uint16_t cid_t;
    const cid_t NO_CID = UINT16_MAX;
};

#endif