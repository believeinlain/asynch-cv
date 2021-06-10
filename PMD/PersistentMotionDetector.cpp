
#include "PersistentMotionDetector.h"

#include "options.h"

#if USE_THREADS
#include <vector>
#include <thread>
#endif

#include <iostream>
using namespace std;

namespace PMD {

    const double PI = 3.14159265358979311600;

    PersistentMotionDetector::PersistentMotionDetector(
        xy_t width, xy_t height, parameters param) : 
        _width(width), _height(height), _param(param),
        _num_parts(param.x_div*param.y_div),
        _partition(width, height, param.x_div, param.y_div),
        _cluster_buffer(),
        _event_buffer(width, height, param.event_buffer_depth, _cluster_buffer)
    {
        // dynamically allocate event handlers since they depend
        // on other members
        _event_handlers = new EventHandler*[_num_parts];
        for (ushort_t i=0; i<param.x_div; ++i) {
            for (ushort_t j=0; j<param.y_div; ++j) {
                _event_handlers[i + j*param.x_div] = new EventHandler(
                    *this, _event_buffer, _cluster_buffer, point(i, j), 
                    _partition.getDomain(i, j), param);
            }
        }

        _framebuffer = nullptr;

        for (cid_t i=0; i<NO_CID; ++i)
            _cluster_colors[i] = color( (float)
                fmod(double(i)*PI*10.0, 360.0), 1.0);

        #if USE_THREADS
            cout<<"Starting PersistentMotionDetector with support for threads :)"<<endl;
            int num_parallel = thread::hardware_concurrency();
            cout<<"Hardware supports up to "<<num_parallel<<" concurrent threads."<<endl;
        #else
            cout<<"Starting PersistentMotionDetector without thread support."<<endl;
            cout<<"Use option \"-D USE_THREADS=1\" to compile with thread support."<<endl;
        #endif
    }
    PersistentMotionDetector::~PersistentMotionDetector() {
        for (uint_t i=0; i<_num_parts; ++i) {
            delete _event_handlers[i];
        }
        delete[] _event_handlers;
    }

    void PersistentMotionDetector::initFramebuffer(byte_t *frame) {
        try 
        {   
            _framebuffer = frame;
            for (uint_t x=0; x<_width; ++x) {
                for (uint_t y=0; y<_height; ++y) {
                    uint_t xy_index = 3*(_width*y + x);
                    cid_t pixel_cid = _event_buffer[point(x, y)].cid;
                    if (pixel_cid == NO_CID) continue;
                    color event_color = _cluster_colors[pixel_cid];
                    for (uint_t z=0; z<3; ++z)
                        _framebuffer[z + xy_index] = event_color[z] / 2;
                }
            }
        }
        catch(const exception& err) 
        {
            cout << "Error initializing framebuffer:" << endl;
            cerr << '\t' << err.what() << endl;
            exit(1);
        }
    }

    void PersistentMotionDetector::processEvents(
        const event *events, uint_t num_events, detection *results) {
        try 
        {
#if USE_THREADS
            // create a vector to manage threads
            vector<thread> event_handler_threads(_num_parts);

            // branch off each event handler to a separate thread to handle events
            for (uint_t i=0; i<_num_parts; ++i)
                // each event handler will loop through events concurrently
                event_handler_threads[i] = thread(
                    &EventHandler::processEventBuffer, _event_handlers[i], 
                    events, num_events);
            
            // rejoin all event handlers
            for (uint_t i=0; i<_num_parts; ++i)
                event_handler_threads[i].join();
#else
            // iterate through the sequence of events
            for (uint_t i=0; i<num_events; ++i) {
                // first place the event
                point place = _partition->placeEvent(events[i].x, events[i].y);
                // then handle the event
                auto k = place.x + place.y*_param.x_div;
                _event_handlers[k]->processEvent(events[i]);
            }
#endif
            detection test;
            test.is_positive = true;
            test.x = 320;
            test.y = 240;
            test.r = 255;
            test.g = 255;
            test.b = 0;

            results[0] = test;
        }
        catch(const exception& err) 
        {
            cout << "Error processing events:" << endl;
            cerr << '\t' << err.what() << endl;
            exit(1);
        }
    }

    void PersistentMotionDetector::drawEvent(event e, cid_t cid) {
        try 
        {
            if (_framebuffer == nullptr) return;

            uint_t xy_index = 3*(_width*e.y + e.x);

            // choose the appropriate color to draw
            color event_color = (cid==NO_CID) ? 
                color(120) : _cluster_colors[cid];

            // draw the event on the framebuffer
            for (uint_t z=0; z<3; ++z) 
                _framebuffer[z + xy_index] = event_color[z];
        } 
        catch(const exception& err) 
        {
            cout << "Error drawing events:" << endl;
            cerr << '\t' << err.what() << endl;
            exit(1);
        }
    }
};
