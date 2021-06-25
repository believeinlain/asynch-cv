
#ifndef _TYPES_H
#define _TYPES_H

#include <limits>
#include <math.h>
#include <algorithm>

namespace PMD {

    // types used to interface with python bindings
    typedef unsigned short xy_t;
    typedef short p_t;
    typedef long long ts_t;

    // ensure bytes are packed tightly since that's how we get events from python
    // #pragma pack(push, 1)
    struct event {
        xy_t x; // 2 bytes
        xy_t y; // 2 bytes
        p_t p; // 2 bytes
        ts_t t; // 8 bytes
    }; // total 14 bytes per event
    // #pragma pack(pop)

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
        uint_t temporal_filter = 5000;
        ushort_t event_buffer_depth = 4;
        ts_t tf = 200000;
        ts_t tc = 200000;
        ushort_t n = 5;
        uint_t buffer_flush_period = 1000;
        uint_t max_cluster_size = 50;
        uint_t num_analyzers = 8;
        uint_t sample_period = 10000;
        ts_t long_duration = 2000000;
        ts_t short_duration = 1000000;
        uint_t ratio_threshold = 100;
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

    template<typename T>
    struct point_t {
        point_t(T x, T y) : x(x), y(y) {}
        point_t() : x(0), y(0) {}
        point_t<T> operator-(const point_t<T> &b) { return point_t<T>(x - b.x, y - b.y); }
        point_t<T> operator+(const point_t<T> &b) { return point_t<T>(x + b.x, y + b.y); }
        T x, y;
    };

    typedef point_t<int> point;
    typedef point_t<double> point_f;

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
            return rect(std::max(tl.x, other.tl.x), std::max(tl.y, other.tl.y),
                std::min(br.x, other.br.x), std::min(br.y, other.br.y));
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

    template<typename T>
    struct buffer_3d {
        const size_t w, h, d;
        buffer_3d(size_t width, size_t height, size_t depth) :
            w(width), h(height), d(depth) {
            _data = new T[width*height*depth]{};
            _top = new size_t[width*height]{};
        }
        ~buffer_3d() {
            delete[] _data;
            delete[] _top;
        }
        T &at(size_t x, size_t y) {
            size_t i_2d = x + y*w;
            return _data[i_2d*d + _top[i_2d]];
        }
        T &at(size_t x, size_t y, size_t z) {
            return _data[(x + y*w)*d + z];
        }
        T push(size_t x, size_t y, const T &value) {
            size_t i_2d = x + y*w;
            _top[i_2d] = (_top[i_2d] + 1) % d;
            T displaced = _data[i_2d*d + _top[i_2d]];
            _data[i_2d*d + _top[i_2d]] = value;
            return displaced;
        }
    private:
        T *_data;
        size_t *_top;
    };

    // max clusters derived from the type size, 
    // so that the only possible invalid id is NO_CID
    typedef unsigned short cid_t;
    const cid_t NO_CID = std::numeric_limits<cid_t>::max();

    // integer types to make interfacing easier,
    // since speed and compactness are not super important here
    struct detection {
        int is_active = 0;
        int x = 0, y = 0;
        int r = 0, g = 0, b = 0;
        int cid = NO_CID;
        float long_v_x = 0, long_v_y = 0;
        float short_v_x = 0, short_v_y = 0;
        int stability = 0;
        float ratio = 0;
    };

};

#endif