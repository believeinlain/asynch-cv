
#ifndef INPUT_QUEUE_H
#define INPUT_QUEUE_H

#include "types.h"

namespace PMD 
{
    class InputQueue {
        int depth;
        int count;
        int front;
        int back;
        event_t *queue;

        InputQueue(int depth);
        ~InputQueue();

        // add an item to the back of the queue
        // will discard the item at the front if full
        void push(event_t e);
        // get the item at the front
        // returns true if successful, false if queue is empty
        bool pop(event_t &out);
    };
};

#endif