
#include "PersistentMotionDetector.h"

#include "options.h"

#include <iostream>
using namespace std;

namespace PMD {

    PersistentMotionDetector::PersistentMotionDetector(
        xy_t width, xy_t height, parameters param) : 
        _width(width), _height(height), _param(param),
        _num_parts(param.x_div*param.y_div),
        _partition(width, height, param.x_div, param.y_div),
        _cluster_buffer(),
        _event_buffer(width, height, param.event_buffer_depth, _cluster_buffer),
        _sorter(_cluster_buffer, param),
        _framebuffer(nullptr)
    {
        // allocate event handlers and cluster analyzers
        _handlers.reserve(_num_parts);
        for (uint_t i=0; i<_num_parts; ++i)
            _handlers.push_back(
                EventHandler(*this, _event_buffer, _cluster_buffer, param));

        _analyzers.reserve(param.num_analyzers);
        for (uint_t i=0; i<param.num_analyzers; ++i)
            _analyzers.push_back(
                ClusterAnalyzer(_sorter, _cluster_buffer, param));
        
        // tell each event handler where it is
        for (ushort_t i=0; i<param.x_div; ++i)
            for (ushort_t j=0; j<param.y_div; ++j)
                _handlers[i + j*param.x_div].setPartitionInfo(
                    point(i, j), _partition.getDomain(i, j));

#if USE_THREADS
            cout<<"Starting PersistentMotionDetector with support for threads :)"<<endl;
            int num_parallel = thread::hardware_concurrency();
            cout<<"Hardware supports up to "<<num_parallel<<" concurrent threads."<<endl;
            // create 2 threads for each usable core
            // this allows for some cpu optimization for core sharing
            // since every thread wont be active all the time
            _threads = new ctpl::thread_pool(num_parallel*2);
            // allocate space for job futures
            _handler_jobs = new future<void>[_num_parts];
#else
            cout<<"Starting PersistentMotionDetector without thread support."<<endl;
            cout<<"Use option \"-D USE_THREADS=1\" to compile with thread support."<<endl;
#endif

    }
    PersistentMotionDetector::~PersistentMotionDetector() {

#if USE_THREADS
        // stop all threads
        _threads->stop();
        // deallocate thread memory
        delete _threads;
        delete[] _handler_jobs;
#endif
    }

    void PersistentMotionDetector::initFramebuffer(byte_t *frame) {
        try 
        {   
            _framebuffer = frame;
            for (uint_t x=0; x<_width; ++x) {
                for (uint_t y=0; y<_height; ++y) {
                    uint_t xy_index = 3*(_width*y + x);
                    cid_t pixel_cid = _event_buffer.at(x, y).top().cid;
                    if (pixel_cid == NO_CID) continue;
                    color event_color = _sorter.getColor(pixel_cid);
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
            // branch off each event handler to a separate thread to handle events
            for (uint_t i=0; i<_num_parts; ++i) {
                EventHandler &handler = _handlers[i];
                // each event handler will loop through events concurrently
                _handler_jobs[i] = _threads->push( [&handler, events, num_events](int id) {
                    handler.processEventBuffer(events, num_events);
                });
            }
            // wait until all tasks finish
            for (uint_t i=0; i<_num_parts; ++i)
                _handler_jobs[i].wait();
#else  
            // handle event buffers sequentially (could alternately sort events here)
            for (uint_t i=0; i<_num_parts; ++i)
                _handlers[i].processEventBuffer(events, num_events);
#endif
            // recalculater cluster priorities
            _sorter.recalculatePriority();

            // analyze the highest priority clusters
            for (uint_t i=0; i<_param.num_analyzers; ++i)
                results[i] = _analyzers[i].updateDetection();
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
// #if USE_THREADS
//             // -- lock buffer for access
//             _framebuffer_access.lock();
// #endif
            if (_framebuffer == nullptr) return;

            uint_t xy_index = 3*(_width*e.y + e.x);

            // choose the appropriate color to draw
            color event_color = _sorter.getColor(cid);

            // draw the event on the framebuffer
            for (uint_t z=0; z<3; ++z) 
                _framebuffer[z + xy_index] = event_color[z];
// #if USE_THREADS
//             // -- release buffer lock
//             _framebuffer_access.unlock();
// #endif
        } 
        catch(const exception& err) 
        {
            cout << "Error drawing events:" << endl;
            cerr << '\t' << err.what() << endl;
            exit(1);
        }
    }
};
