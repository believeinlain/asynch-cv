
#ifndef _TYPES_H
#define _TYPES_H

typedef unsigned short xy_t;
typedef signed char polarity_t;
typedef unsigned long long timestamp_t;

typedef signed int xy_sum_t;
typedef float xy_float_t;
typedef unsigned int cluster_weight_t;

struct color {
    color(unsigned char r, unsigned char g, unsigned char b) :
        r(r), g(g), b(b) {}
    color() : r(0), g(0), b(0) {}
    unsigned char r, g, b;
};

struct point {
    xy_t x, y;
};
    
struct event {
    xy_t x, y;
    polarity_t p;
    timestamp_t t;
};

template <class T>
class array_2d {
    int size;
    int width;
    T *elements;
public:
    array_2d(int width, int height) : size(width*height), width(width) {
        this->elements = new T[this->size];
    }
    array_2d(int width, int height, T *data) : size(width*height), width(width) {
        this->elements = data;
    }
    ~array_2d() {
        delete this->elements;
    }
    void put(int i, int j, T val) {
        this->elements[i+j*this->width] = val;
    }
    T get(int i, int j) {
        return this->elements[i+j*this->width];
    }
};

#endif