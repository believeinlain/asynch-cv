
from random import random
from math import exp
from enum import Enum
import numpy as np
from PMD.InputQueue import *
from PMD.EventBuffer import *
from PMD.ClusterBuffer import *

class EventHandlerResult(Enum):
    REJECTED = 0
    FILTERED = 1
    CLUSTERED = 2

class EventHandler:
    def __init__(self, domain, input_queue: InputQueue, event_buffer: EventBuffer, cluster_buffer: ClusterBuffer, parameters):
        # create empty dict if no parameters passed
        if parameters is None:
            parameters = {}
        # allows a minimum portion of events through regardless of prior event density
        self._a = parameters.get('a', 0.95)
        # controls pre-filter sensitivity
        self._b = parameters.get('b', 0.8)
        # how far back in time to consider events for filtering
        self._tf = parameters.get('tf', 150_000)
        # minimum number of correlated events required to allow a particular event through the filter
        self._n = parameters.get('n', 4)
        # how far back in time to consider events for clustering
        self._tc = parameters.get('tc', 150_000)

        self._domain = domain
        self._input_queue = input_queue
        self._event_buffer = event_buffer
        self._cluster_buffer = cluster_buffer
        self._acc = 0
        self._dt = 0
        self._last_t = 0

    def tick(self, sys_time, event_callback):
        # reset prefilter accumulator and dt
        self._acc = 0
        self._dt = 0

        # handle all events in queue
        while True:
            e = self._input_queue.pop()
            if e is None:
                break
            x, y, _, t = e

            # add the time between events to dt
            self._dt += t-self._last_t
            self._last_t = t
            # compute density (events per millisecond)
            dt_ms = self._dt//1_000
            m = (self._acc / dt_ms) if dt_ms > 0 else 0

            # prefilter stage
            if random() < self._a*(1-exp(-self._b*m)):
                event_callback(e, EventHandlerResult.REJECTED)
                continue
            
            (num_correlated, adjacent) = self._event_buffer.check_vicinity(x, y, t, self._tf, self._tc)

            # correlational filter stage
            if num_correlated < self._n:
                self._event_buffer.add_event(x, y, t)
                event_callback(e, EventHandlerResult.FILTERED)
                continue
            
            # segmentation stage
            if adjacent.size == 1:
                assigned = adjacent[0]
            elif adjacent.size > 1:
                # find the oldest adjacent region
                birth_order = self._cluster_buffer.get_birth_order(adjacent)
                assigned = adjacent[birth_order]
            else:
                assigned = self._cluster_buffer.create_new_cluster(x, y, t)
            
            # add the event to the event buffer
            self._event_buffer.add_event(x, y, t, assigned)
            # add the event to the cluster buffer
            self._cluster_buffer.add_event(x, y, assigned)

            event_callback(e, EventHandlerResult.CLUSTERED, assigned)
        
        # remove expired events
        u_ids, u_x, u_y = self._event_buffer.remove_expired_events(self._domain, sys_time - self._tc)
        self._cluster_buffer.remove_events(u_ids, u_x, u_y)