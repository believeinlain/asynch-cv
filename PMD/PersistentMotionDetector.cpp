
#include "PersistentMotionDetector.h"

#include "options.h"

#if USE_THREADS
#include <thread>
#include <vector>
#endif

#include <iostream>

using namespace std;

namespace PMD {

    const double PI = 3.1415927;

    PersistentMotionDetector::PersistentMotionDetector(xy_t width, xy_t height, parameters param) : 
        width(width), height(height), param(param)
    {
        this->num_parts = param.x_div*param.y_div;

        this->partition = new Partition(width, height, param.x_div, param.y_div);
        this->event_buffer = new EventBuffer(width, height, param.event_buffer_depth);
        this->cluster_buffer = new ClusterBuffer();
        this->event_handlers = new EventHandler*[this->num_parts];
        for (uint_t i=0; i<param.x_div; i++) {
            for (uint_t j=0; j<param.y_div; j++) {
                this->event_handlers[i + j*param.x_div] = new EventHandler(
                    this, this->event_buffer, this->cluster_buffer, point(i, j), 
                    this->partition->get_domain(i, j), param);
            }
        }

        this->framebuffer = nullptr;

        for (cid_t i=0; i<UNASSIGNED_CLUSTER; i++)
            cluster_colors[i] = color(fmod(double(i)*PI*10.0, 360.0), 1.0);

        #if USE_THREADS
            cout<<"Starting PersistentMotionDetector with support for threads :)"<<endl;
        #else
            cout<<"Starting PersistentMotionDetector without thread support."<<endl;
            cout<<"Use option \"-D USE_THREADS=1\" to compile with thread support."<<endl;
        #endif
    }
    PersistentMotionDetector::~PersistentMotionDetector() {
        delete this->partition;
        delete this->event_buffer;
        delete this->cluster_buffer;
        for (uint_t i=0; i<this->num_parts; i++) {
            delete this->event_handlers[i];
        }
        delete[] this->event_handlers;
    }

    void PersistentMotionDetector::init_framebuffer(byte_t *frame) {
        this->framebuffer = frame;
        cid_t pixel_cid;
        color event_color;
        uint_t xy_index;
        for (uint_t x=0; x<this->width; x++) {
            for (uint_t y=0; y<this->height; y++) {
                xy_index = 3*(this->width*y + x);
                pixel_cid = this->event_buffer->get_cid_at(x, y);
                if (pixel_cid == UNASSIGNED_CLUSTER) continue;
                event_color = this->cluster_colors[pixel_cid];
                for (uint_t z=0; z<3; z++)
                    this->framebuffer[z + xy_index] = event_color[z] / 2;
            }
        }
    }

    void PersistentMotionDetector::process_events(const event *events, uint_t num_events) {
#if USE_THREADS
        // create a vector to manage threads
        vector<thread> event_handler_threads(this->num_parts);
        // branch off each event handler to a separate thread to handle events
        for (uint_t i=0; i<this->num_parts; i++) {
            // each event handler will loop through events concurrently
            event_handler_threads[i] = thread(
                &EventHandler::process_event_buffer, this->event_handlers[i], events, num_events);
        }
        // rejoin all event handlers
        for (uint_t i=0; i<this->num_parts; i++) {
            event_handler_threads[i].join();
        }
#else
        point place;

        // iterate through the sequence of events
        for (uint_t i=0; i<num_events; i++) {
            const event &e = events[i];
            // first place the event
            place = this->partition->place_event(e.x, e.y);
            // then handle the event
            this->event_handlers[place.x + place.y*this->param.x_div]->process_event(e);
        }
#endif
    }

    void PersistentMotionDetector::event_callback(const event &e, cid_t cid) {
        if (this->framebuffer == nullptr) return;

        const uint_t xy_index = 3*(this->width*e.y + e.x);
        color event_color;

        if (cid==UNASSIGNED_CLUSTER) event_color = color(120);
        else event_color = this->cluster_colors[cid];

        for (uint_t z=0; z<3; z++) this->framebuffer[z + xy_index] = event_color[z];
    }
};
