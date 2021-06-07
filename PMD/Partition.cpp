
#include "Partition.h"

namespace PMD {
    Partition::Partition(xy_t width, xy_t height, xy_t x_div, xy_t y_div) : 
        width(width), height(height), x_div(x_div), y_div(y_div) 
    {
        this->x_bounds = new xy_t[x_div-1];
        for (xy_t i=0; i<(x_div-1); i++) {
            this->x_bounds[i] = (width/x_div)*(i+1);
        }

        this->y_bounds = new xy_t[y_div-1];
        for (xy_t i=0; i<(y_div-1); i++) {
            this->y_bounds[i] = (height/y_div)*(i+1);
        }
    }
    Partition::~Partition() {
        delete[] this->x_bounds;
        delete[] this->y_bounds;
    }

    rect Partition::get_domain(xy_t place_x, xy_t place_y) {
        xy_t d_width = this->width/this->x_div;
        xy_t d_height = this->height/this->y_div;
        return rect(
            d_width*(place_x),
            d_height*(place_y),
            d_width*(place_x+1),
            d_height*(place_y+1)
        );
    }
#if !USE_THREADS
    point Partition::place_event(xy_t x, xy_t y) {
        point dest;
        xy_t i;

        for (i=0; i<(x_div-1); i++)
            if (this->x_bounds[i] > x) 
                break;
        dest.x = i;

        for (i=0; i<(y_div-1); i++)
            if (this->y_bounds[i] > y) 
                break;
        dest.y = i;

        return dest;
    }
#endif
};