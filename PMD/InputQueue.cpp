
#include "InputQueue.h"

namespace PMD {
    InputQueue::InputQueue(uint_t depth) :
        depth(depth), count(0), front(0), back(0) 
    {
        this->queue = new event[depth];
    }
    InputQueue::~InputQueue() {
        delete this->queue;
    }

    void InputQueue::push(event e) {
        this->queue[this->back] = e;
        this->back = (this->back + 1) % this->depth;

        if (this->count < this->depth)
            this->count++;
    }

    bool InputQueue::pop(event &out) {
        if (this->count > 0) {
            out = this->queue[this->front];
            this->front = (this->front + 1) % this->depth;
            this->count--;
            return true;
        }
        return false;
    }

    const event *InputQueue::peek() {
        if (this->count > 0) return &this->queue[this->front];
        return nullptr;
    }
};