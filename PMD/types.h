
#ifndef _TYPES_H
#define _TYPES_H

#include <limits>
#include <math.h>
#include <algorithm>

using std::min;
using std::max;

namespace PMD {

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
    
    // general unsigned integer shorthands
    typedef unsigned int uint_t;
    typedef unsigned int ushort_t;

    // execution parameters
    struct parameters {
        uint_t width;
        uint_t height;
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
        uint_t sample_period = 10000;
        ts_t sample_duration = 320000;
    };

    struct color {
        // rgb, int from 0 tp 255
        color(byte_t r, byte_t g, byte_t b) :
            r(r), g(g), b(b) {}
        // hue - float from 0.0 to 360.0, vibrance - float from 0 to 1
        color(double h, double v) {
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
        // allow indexing as an array (bgr order)
        byte_t &operator[](uint_t index) {
            if (index == 1) return g;
            else if (index == 2) return r;
            else return b;
        }
    };

    struct point {
        point(int x, int y) : x(x), y(y) {}
        point() : x(0), y(0) {}
        int x, y;
    };

    struct rect {
        rect(int tlx, int tly, int brx, int bry) : 
            tl(tlx, tly), br(brx, bry), 
            width(brx - tlx), height(bry - tly) {}
        const point tl, br;
        const unsigned int width, height;
        inline bool contains(int x, int y) const {
            return (tl.x <= x) 
                && (tl.y <= y) 
                && (x < br.x) 
                && (y < br.y);
        }
        inline rect intersection(const rect other) const {
            return rect(max(tl.x, other.tl.x), max(tl.y, other.tl.y),
                min(br.x, other.br.x), min(br.y, other.br.y));
        }
    };

    template<typename T>
    struct array_2d {
        const size_t w, h;
        array_2d(size_t width, size_t height) :
            w(width), h(height) {
            _data = new T[width*height]{};
        }
        ~array_2d() {
            delete[] _data;
        }
        T &at(size_t x, size_t y) {
            return _data[x + y*w];
        }
    private:
        T *_data;
    };

    // max clusters derived from the type size, 
    // so that the only possible invalid id is NO_CID
    typedef unsigned short cid_t;
    const cid_t NO_CID = USHRT_MAX;

    // integer types to make interfacing easier,
    // since speed and compactness are not super important here
    struct detection {
        int is_positive = 0;
        int x = 0, y = 0;
        int r = 0, g = 0, b = 0;
        int cid = NO_CID;
    };

};

#endif