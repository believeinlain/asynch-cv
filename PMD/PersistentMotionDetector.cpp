
#include "PersistentMotionDetector.h"

#include <iostream>

namespace PMD {
    PersistentMotionDetector::PersistentMotionDetector(xy_t width, xy_t height, parameters param) : 
        width(width), height(height), param(param)
    {
        this->num_parts = param.x_div*param.y_div;

        this->partition = new Partition(width, height, param.x_div, param.y_div);
        this->input_queues = new InputQueue*[param.x_div*param.y_div];
        this->event_handlers = new EventHandler*[param.x_div*param.y_div];
        for (uint_t i=0; i<this->num_parts; i++) {
            this->input_queues[i] = new InputQueue(param.input_queue_depth);
            this->event_handlers[i] = new EventHandler(this, this->input_queues[i], param.events_per_ms);
        }

        this->framebuffer = nullptr;
    }
    PersistentMotionDetector::~PersistentMotionDetector() {
        delete this->partition;
        for (uint_t i=0; i<this->num_parts; i++) {
            delete this->input_queues[i];
            delete this->event_handlers[i];
        }
        delete this->input_queues;
        delete this->event_handlers;
    }

    void PersistentMotionDetector::init_framebuffer(byte_t *frame) {
        this->framebuffer = frame;
    }

    void PersistentMotionDetector::input_events(const event *events, uint_t num_events) {
        for (uint_t i=0; i<num_events; i++) {
            const event &e = events[i];
            point place = this->partition->place_event(e.x, e.y);
            this->input_queues[place.x + place.y*this->param.x_div]->push(e);
        }
    }

    void PersistentMotionDetector::process_until(timestamp_t time_us) {
        for (uint_t i=0; i<this->num_parts; i++) 
            this->event_handlers[i]->process_until(time_us);
    }

    void PersistentMotionDetector::draw_event(const event &e) {
        if (this->framebuffer == nullptr) return;
        byte_t c = e.p*255;
        for (uint_t z=0; z<3; z++) this->framebuffer[z + 3*(this->width*e.y + e.x)] = c;
    }
};
