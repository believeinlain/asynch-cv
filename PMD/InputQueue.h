
#ifndef _INPUT_QUEUE_H
#define _INPUT_QUEUE_H

#include "types.h"

namespace PMD {
    class InputQueue {
        uint_t depth;
        uint_t count;
        uint_t front;
        uint_t back;
        event *queue;

    public:
        InputQueue(uint_t depth);
        ~InputQueue();

        // add an item to the back of the queue
        // will discard the item at the front if full
        void push(event e);
        // get the item at the front
        // returns true if successful, false if queue is empty
        bool pop(event &out);
        // look at the event in front
        // returns nullptr if queue is empty
        const event *peek();
    };
};

#endif