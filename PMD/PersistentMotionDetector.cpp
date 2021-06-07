
#include "PersistentMotionDetector.h"

namespace PMD {
    PersistentMotionDetector::PersistentMotionDetector(xy_t width, xy_t height, parameters param) : 
        width(width), height(height), param(param)
    {
        this->num_parts = param.x_div*param.y_div;

        this->partition = new Partition(width, height, param.x_div, param.y_div);
        this->event_buffer = new EventBuffer(width, height, param.event_buffer_depth);
        this->event_handlers = new EventHandler*[param.x_div*param.y_div];
        for (uint_t i=0; i<this->num_parts; i++)
            this->event_handlers[i] = new EventHandler(this, this->event_buffer, param);

        this->framebuffer = nullptr;
    }
    PersistentMotionDetector::~PersistentMotionDetector() {
        delete this->partition;
        for (uint_t i=0; i<this->num_parts; i++) 
            delete this->event_handlers[i];
        delete[] this->event_handlers;
    }

    void PersistentMotionDetector::init_framebuffer(byte_t *frame) {
        this->framebuffer = frame;
    }

    void PersistentMotionDetector::process_events(const event *events, uint_t num_events) {
        point place;
        ts_t time;

        // iterate through the sequence of events
        for (uint_t i=0; i<num_events; i++) {
            const event &e = events[i];
            // update the simulation time
            time = e.t;
            // first place the event
            place = this->partition->place_event(e.x, e.y);
            // handle the event
            this->event_handlers[place.x + place.y*this->param.x_div]->process_event(e);
        }
    }

    void PersistentMotionDetector::event_callback(const event &e, bool is_filtered, cid_t cluster) {
        if (this->framebuffer == nullptr) return;
        const uint_t xy_index = 3*(this->width*e.y + e.x);
        color event_color;
        if (is_filtered) event_color = color(120);
        else event_color = color(e.p*255);
        for (uint_t z=0; z<3; z++) this->framebuffer[z + xy_index] = event_color[z];
    }
};
