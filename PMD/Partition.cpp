
#include "Partition.h"

namespace PMD {
    Partition::Partition(xy_t width, xy_t height, xy_t x_div, xy_t y_div) : 
        width(width), height(height), x_div(x_div), y_div(y_div) 
    {
        this->x_bounds = new xy_t[x_div-1];
        for (int i=0; i<(x_div-1); i++) {
            this->x_bounds[i] = (width/x_div)*(i+1);
        }

        this->y_bounds = new xy_t[y_div-1];
        for (int i=0; i<(y_div-1); i++) {
            this->y_bounds[i] = (height/y_div)*(i+1);
        }
    }
    Partition::~Partition() {
        delete this->x_bounds;
        delete this->y_bounds;
    }

    point Partition::place_event(xy_t x, xy_t y) {
        point dest;
    }
};