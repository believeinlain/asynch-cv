
#ifndef _TYPES_H
#define _TYPES_H

#include <cstdint>
#include <math.h>

namespace PMD {
    
    // choose the fastest types for xy positions and timestamps
    typedef uint_fast16_t xy_t;
    typedef uint_fast64_t ts_t;

    // types carefully chosen to fit 4-byte alignment
    // this is important because of how it interfaces with python
    struct event {
        uint16_t x; // 2 bytes
        uint16_t y; // 2 bytes
        int32_t p; // 4 bytes
        uint64_t t; // 8 bytes
    }; // total 16 bytes per event

    // this is used to access the framebuffer, so it's important to be a single byte
    typedef uint8_t byte_t;
    // choose fast types for different sized values
    typedef int_fast8_t uchar_t;
    typedef uint_fast16_t ushort_t;
    typedef uint_fast32_t uint_t;
    typedef uint_fast64_t ulong_t;

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
        inline byte_t &operator[](uchar_t index) {
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
        rect() {}
        point tl, br;
        inline bool contains(const xy_t &x, const xy_t &y) {
            return (this->tl.x <= x) 
                && (this->tl.y <= y) 
                && (x < this->br.x) 
                && (y < this->br.y);
        }
    };

    typedef uint16_t cid_t;
    const cid_t UNASSIGNED_CLUSTER = UINT16_MAX;
};

#endif