
#include "InputQueue.h"

namespace PMD {
    InputQueue::InputQueue(int depth) :
        depth(depth), count(0), front(0), back(0) 
    {
        this->queue = new event[depth];
    }
    InputQueue::~InputQueue() {
        delete this->queue;
    }

    // add an item to the back of the queue
    // will discard the item at the front if full
    void InputQueue::push(event e) {
        this->queue[this->back] = e;
        this->back = (this->back + 1) % this->depth;

        if (this->count < this->depth)
            this->count++;
    }

    // get the item at the front
    // returns true if successful, false if queue is empty
    bool InputQueue::pop(event &out) {
        if (this->count > 0) {
            out = this->queue[this->front];
            this->front = (this->front + 1) % this->depth;
            this->count--;
            return true;
        }
        return false;
    }
};