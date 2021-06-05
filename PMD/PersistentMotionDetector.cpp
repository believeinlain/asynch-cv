
#include "PersistentMotionDetector.h"

namespace PMD {
    PersistentMotionDetector::PersistentMotionDetector(xy_t width, xy_t height, parameters param) : 
        width(width), height(height), param(param), input_queues(param.x_div, param.y_div)
    {
        this->num_partitions = param.x_div*param.y_div;

        this->partition = new Partition(width, height, param.x_div, param.y_div);

        for (int i=0; i<param.x_div; i++)
            for (int j=0; j<param.y_div; j++)
                this->input_queues.put(i, j, new InputQueue(param.input_queue_depth));
    }
    PersistentMotionDetector::~PersistentMotionDetector() {
        delete this->partition;
        for (int i=0; i<param.x_div; i++)
            for (int j=0; j<param.y_div; j++)
                delete this->input_queues.get(i, j);
    }

    void PersistentMotionDetector::update_frame(array_2d<color> &start_frame, event events[], int num_events) {
        for (int i=0; i<num_events; i++) {
            event e = events[i];
            point place = this->partition->place_event(e.x, e.y);
            this->input_queues.get(place.x, place.y)->push(e);
        }
        
        for (int i=0; i<this->param.x_div; i++)
            for (int j=0; j<this->param.y_div; j++) {
                event e;
                if (this->input_queues.get(i, j)->pop(e)) {
                    color c = color(e.p*255, e.p*255, e.p*255);
                    start_frame.put(e.y, e.x, c);
                }
        }
    }
};
