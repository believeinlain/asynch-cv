
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
            this->event_handlers[i] = new EventHandler(this, this->input_queues[i], param);
        }

        this->framebuffer = nullptr;
    }
    PersistentMotionDetector::~PersistentMotionDetector() {
        delete this->partition;
        for (uint_t i=0; i<this->num_parts; i++) {
            delete this->input_queues[i];
            delete this->event_handlers[i];
        }
        delete[] this->input_queues;
        delete[] this->event_handlers;
    }

    void PersistentMotionDetector::init_framebuffer(byte_t *frame) {
        this->framebuffer = frame;
    }

    uint_t PersistentMotionDetector::input_events_until(
            ts_t time_us, const event *events, uint_t num_events, uint_t start_at) {
        for (uint_t i=start_at; i<num_events; i++) {
            const event &e = events[i];
            // return the last event processed if we're over time
            if (e.t > time_us) return i;
            point place = this->partition->place_event(e.x, e.y);
            this->input_queues[place.x + place.y*this->param.x_div]->push(e);
        }
        return num_events - 1;
    }

    void PersistentMotionDetector::process_until(ts_t time_us) {
        for (uint_t i=0; i<this->num_parts; i++) 
            this->event_handlers[i]->process_until(time_us);
    }

    void PersistentMotionDetector::event_callback(const event &e, bool is_filtered, cid_t cluster) {
        if (this->framebuffer == nullptr) return;
        const uint_t xy_index = 3*(this->width*e.y + e.x);
        color event_color;
        if (is_filtered) event_color = color(100);
        else event_color = color(e.p*255);
        for (uint_t z=0; z<3; z++) this->framebuffer[z + xy_index] = event_color[z];
    }
};
