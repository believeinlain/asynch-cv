
#include "PersistentMotionDetector.h"

#include <iostream>

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

    void PersistentMotionDetector::process_events(byte_t *frame, const event *events, int num_events) {
        for (int i=0; i<num_events; i++) {
            const event &e = events[i];
            point place = this->partition->place_event(e.x, e.y);
            // std::cout << "Placed event at " << place.x << ',' << place.y << " \n";
            this->input_queues.get(place.x, place.y)->push(e);
        }

        for (int i=0; i<this->param.x_div; i++)
            for (int j=0; j<this->param.y_div; j++) {
                event e;
                while (this->input_queues.get(i, j)->pop(e))
                    this->draw_event(frame, e);
        }
    }

    void PersistentMotionDetector::draw_event(byte_t *frame, const event &e) {
        byte_t c = e.p*255;
        for (int z=0; z<3; z++) frame[z + 3*(this->width*e.y + e.x)] = c;
    }
};
