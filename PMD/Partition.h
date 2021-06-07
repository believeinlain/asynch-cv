
#ifndef _PARTITION_H
#define _PARTITION_H

#include "types.h"

namespace PMD {
    class Partition {
        xy_t width, height;
        xy_t x_div, y_div;
        xy_t *x_bounds, *y_bounds;

    public:
        Partition(xy_t width, xy_t height, xy_t x_div, xy_t y_div);
        ~Partition();

        rect get_domain(xy_t place_x, xy_t place_y);

        point place_event(xy_t x, xy_t y);
    };
};

#endif
