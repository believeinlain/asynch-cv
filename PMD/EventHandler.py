
from enum import Enum
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
        # how far back in time to consider events for filtering
        self._tf = parameters.get('tf', 150_000)
        # minimum number of correlated events required to allow a particular event through the filter
        self._n = parameters.get('n', 4)
        # how far back in time to consider events for clustering
        self._tc = parameters.get('tc', 150_000)
        self._merge_clusters = parameters.get('merge_clusters', False)
        self._temporal_filter = parameters.get('temporal_filter', 1_000)

        self._domain = domain
        self._input_queue = input_queue
        self._event_buffer = event_buffer
        self._cluster_buffer = cluster_buffer

    def tick(self, sys_time, event_callback):
        """Called by PersistentMotionDetector.tick_all"""
        # handle all events in queue
        while True:
            e = self._input_queue.pop()
            if e is None:
                break
            x, y, _, t = e

            # temporal filter stage
            if t-self._event_buffer.get_ts_buffer_top(x, y) < self._temporal_filter:
                event_callback(e, EventHandlerResult.REJECTED)
                continue
            
            (num_correlated, adjacent) = self._event_buffer.check_vicinity(x, y, t, self._tf, self._tc)

            # correlational filter stage
            if num_correlated < self._n:
                u_ids, u_x, u_y = self._event_buffer.add_event(x, y, t)
                event_callback(e, EventHandlerResult.FILTERED)

            else:
                # segmentation stage
                if adjacent.size == 1:
                    assigned = adjacent[0]
                elif adjacent.size > 1:
                    # find the oldest adjacent region
                    birth_order = self._cluster_buffer.get_birth_order(adjacent)
                    assigned = adjacent[birth_order][0]
                    # merge if desired
                    if self._merge_clusters:
                        self._event_buffer.merge_clusters(adjacent[birth_order])
                        self._cluster_buffer.merge_clusters(adjacent[birth_order])
                else:
                    assigned = self._cluster_buffer.create_new_cluster(t)
                
                # add the event to the event buffer
                u_ids, u_x, u_y = self._event_buffer.add_event(x, y, t, assigned)
                # add the event to the cluster buffer
                self._cluster_buffer.add_event(x, y, assigned)

                event_callback(e, EventHandlerResult.CLUSTERED, assigned)
            
            # remove displaced event(s)
            self._cluster_buffer.remove_events(u_ids, u_x, u_y)
        
        # remove expired events in domain
        u_ids, u_x, u_y = self._event_buffer.remove_expired_events(self._domain, sys_time - self._tc)
        self._cluster_buffer.remove_events(u_ids, u_x, u_y)