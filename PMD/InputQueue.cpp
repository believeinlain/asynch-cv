
#include "InputQueue.h"

namespace PMD {
    InputQueue::InputQueue(int depth) {
        this->depth = depth;
        this->count = 0;
        this->front = 0;
        this->back = 0;
        this->queue = new event_t[depth];
    }
    InputQueue::~InputQueue() {
        delete this->queue;
    }

    // add an item to the back of the queue
    // will discard the item at the front if full
    void InputQueue::push(event_t e) {
        this->queue[this->back] = e;
        this->back = (this->back + 1) % this->depth;

        if (this->count < this->depth)
            this->count = this->count + 1;
    }

    // get the item at the front
    // returns true if successful, false if queue is empty
    bool InputQueue::pop(event_t &out) {
        if (this->count > 0) {
            out = this->queue[this->front];
            this->count++;
            this->front = (this->front + 1) % this->depth;
            return true;
        }
        return false;
    }
};