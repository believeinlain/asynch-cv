
#ifndef _PARTITION_H
#define _PARTITION_H

#include "types.h"
#include "options.h"

namespace PMD {
    class Partition {
        xy_t _width, _height;
        ushort_t _x_div, _y_div;
        xy_t *_x_bounds, *_y_bounds;

    public:
        Partition(
            xy_t width, xy_t height, ushort_t x_div, ushort_t y_div);
        ~Partition();

        rect getDomain(ushort_t place_x, ushort_t place_y);
#if !USE_THREADS
        point place_event(xy_t x, xy_t y);
#endif
    };
};

#endif
