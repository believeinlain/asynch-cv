
#ifndef _TYPES_H
#define _TYPES_H

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
    color() : r(0), g(0), b(0) {}
    byte_t r, g, b;
};

struct point {
    xy_t x, y;
};

struct rect {
    point tl, br;
};


struct detection {
    bool is_positive;
    point position;
    point velocity;
    float confidence;
};

enum event_result {
    EVENT_REJECTED,
    EVENT_FILTERED,
    EVENT_CLUSTERED
};

struct processed_event {
    point position;
    event_result result;
    color c;
};

template <class T>
class array_2d {
    uint_t size;
    uint_t width;
    T *elements;
public:
    array_2d(uint_t width, uint_t height) : size(width*height), width(width) {
        this->elements = new T[this->size];
    }
    array_2d(uint_t width, uint_t height, T *data) : size(width*height), width(width) {
        this->elements = data;
    }
    ~array_2d() {
        delete this->elements;
    }
    void put(uint_t i, uint_t j, T val) {
        this->elements[i+j*this->width] = val;
    }
    T get(uint_t i, uint_t j) {
        return this->elements[i+j*this->width];
    }
};

#endif