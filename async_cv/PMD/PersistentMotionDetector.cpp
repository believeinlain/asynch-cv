
#include "PersistentMotionDetector.h"

#include "options.h"

#include <iostream>
using namespace std;

namespace PMD {

    PersistentMotionDetector::PersistentMotionDetector(parameters p) : 
        _p(p), _bounds(0, 0, p.width, p.height), _num_parts(p.x_div*p.y_div), 
        _cluster_buffer(),
        _event_buffer(p.width, p.height, p.event_buffer_depth, _cluster_buffer),
        _sorter(_cluster_buffer, p)
    {
        // allocate event handlers and cluster analyzers
        _handlers.reserve(_num_parts);
        for (ushort_t i=0; i<p.x_div; ++i)
            for (ushort_t j=0; j<p.y_div; ++j)
                _handlers.push_back(
                    EventHandler(*this, _event_buffer, _cluster_buffer, point(i, j), p));

        _analyzers.reserve(p.num_analyzers);
        for (uint_t i=0; i<p.num_analyzers; ++i)
            _analyzers.push_back(
                ClusterAnalyzer(_sorter, _cluster_buffer, p));

#if USE_THREADS
            cout<<"Starting PersistentMotionDetector with support for threads :)"<<endl;
            int num_parallel = thread::hardware_concurrency();
            cout<<"Hardware supports up to "<<num_parallel<<" concurrent threads."<<endl;
            // create a thread for each usable core
            _threads = new ctpl::thread_pool(num_parallel);
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
            for (uint_t x=0; x<_bounds.width; ++x) {
                for (uint_t y=0; y<_bounds.height; ++y) {
                    uint_t xy_index = 3*(_bounds.width*y + x);
                    cid_t pixel_cid = _event_buffer.at(x, y).cid;
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

    void PersistentMotionDetector::simulate(
        const event *events, uint_t num_events, detection *results, cid_t *indices) {
        try 
        {
            // identify events from the start of this buffer to last sample time + sample period
            uint_t start_event = 0;
            uint_t end_event = 0;

            // loop through events, one sample period at a time
            do {
                // cout << "Entered sample loop: start_event " << start_event << endl;
                while (end_event < num_events && events[end_event].t < _last_sample_time + _p.sample_period) {
                    // update sample time
                    _last_sample_time = events[end_event].t;
                    ++end_event;
                }
                // if no events captured, reset sample time
                if (end_event == start_event) {
                    _last_sample_time = events[start_event].t;
                    continue;
                }
                // sample_end_event now represents the index of the first event in the next sample period

                // process the events in the current sample
                processEvents(events + start_event, end_event - start_event);

                // sample cluster centroids
                for (uint_t i=0; i<_p.num_analyzers; ++i) 
                    _analyzers[i].sampleCluster(_last_sample_time);
                
                // advance the start event to the next sample
                start_event = end_event;

            } while (start_event < num_events);

            // recalculate cluster priorities and update analysis results
            _sorter.recalculatePriority();
            for (uint_t i=0; i<_p.num_analyzers; ++i) {
                _analyzers[i].reassignCluster();
                results[i] = _analyzers[i].updateDetection();
            }

            // draw the index map
            for (size_t x=0; x<_bounds.width; ++x)
                for (size_t y=0; y<_bounds.height; ++y)
                    indices[x + y*_bounds.width] = _event_buffer.at(x, y).cid;
        }
        catch(const exception& err) 
        {
            cout << "Error processing events:" << endl;
            cerr << '\t' << err.what() << endl;
            exit(1);
        }
    }

    void PersistentMotionDetector::processEvents(const event *events, uint_t num_events) {
#if USE_THREADS
        // branch off each event handler to a separate thread to handle events
        for (uint_t i=0; i<_num_parts; ++i) {
            EventHandler &handler = _handlers[i];
            // each event handler will loop through events concurrently
            _handler_jobs[i] = _threads->push( [&handler, events, num_events](int id) {
                handler.processEventBuffer(events, num_events);
            });
        }
        // wait until all event processing tasks finish
        for (uint_t i=0; i<_num_parts; ++i)
            _handler_jobs[i].wait();
#else  
        // handle event buffers sequentially (could alternately sort events here)
        for (uint_t i=0; i<_num_parts; ++i)
            _handlers[i].processEventBuffer(events, num_events);
#endif
    }

    void PersistentMotionDetector::drawEvent(event e, cid_t cid) {
        try 
        {
            if (_framebuffer == nullptr) return;

            uint_t xy_index = 3*(_bounds.width*e.y + e.x);

            // choose the appropriate color to draw
            color event_color = _sorter.getColor(cid);

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
