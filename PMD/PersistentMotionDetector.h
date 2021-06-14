
#ifndef _PERSISTENT_MOTION_DETECTOR_H
#define _PERSISTENT_MOTION_DETECTOR_H

#include "types.h"
#include "EventHandler.h"
#include "EventBuffer.h"
#include "ClusterBuffer.h"
#include "ClusterSorter.h"
#include "ClusterAnalyzer.h"

#if USE_THREADS
#include <ctpl_stl.h>
#include <functional>
#include <thread>
#include <mutex>
#endif

#include <vector>

namespace PMD {

    class PersistentMotionDetector {
        // friend so event handler can draw events
        friend class EventHandler;

        const parameters _p;
        const uint_t _num_parts;
        const rect _bounds;

        std::vector<EventHandler> _handlers;
        EventBuffer _event_buffer;
        ClusterBuffer _cluster_buffer;
        ClusterSorter _sorter;
        std::vector<ClusterAnalyzer> _analyzers;

        byte_t *_framebuffer;
        std::vector<detection> _results;

        #if USE_THREADS
        ctpl::thread_pool *_threads;
        std::future<void> *_handler_jobs;
        std::mutex _framebuffer_access;
        #endif

    public:
        PersistentMotionDetector(parameters p);
        ~PersistentMotionDetector();

        void initFramebuffer(byte_t *frame);
        void processEvents(const event *events, uint_t num_events, detection *results, cid_t *indices);

    protected:
        void drawEvent(event e, cid_t cid);
    };
};

#endif
