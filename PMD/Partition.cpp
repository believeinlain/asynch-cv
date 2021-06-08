
#include "Partition.h"

namespace PMD {
    Partition::Partition(
        xy_t width, xy_t height, ushort_t x_div, ushort_t y_div) : 
        _width(width), _height(height), _x_div(x_div), _y_div(y_div) 
    {
        _x_bounds = new xy_t[x_div-1];
        for (ushort_t i=0; i<(x_div-1); ++i)
            _x_bounds[i] = (width/x_div)*(i+1);

        _y_bounds = new xy_t[y_div-1];
        for (ushort_t i=0; i<(y_div-1); ++i)
            _y_bounds[i] = (height/y_div)*(i+1);
    }
    Partition::~Partition() {
        delete[] _x_bounds;
        delete[] _y_bounds;
    }

    rect Partition::getDomain(ushort_t place_x, ushort_t place_y) {
        xy_t d_width = _width/_x_div;
        xy_t d_height = _height/_y_div;
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
        ushort_t i
        for (i=0; i<(x_div-1); ++i)
            if (_x_bounds[i] > x) break;
        dest.x = i;

        for (i=0; i<(y_div-1); ++i)
            if (_y_bounds[i] > y) break;
        dest.y = i;

        return dest;
    }
#endif
};