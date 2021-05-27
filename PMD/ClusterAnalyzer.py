
import numpy as np
from PMD.ClusterBuffer import *
from PMD.ClusterPriorityModule import *
from PMD.EventBuffer import *

class ClusterAnalyzer:
    def __init__(self, priority, cluster_priority_module: ClusterPriorityModule, cluster_buffer: ClusterBuffer, event_buffer: EventBuffer):
        self._priority = priority
        self._cluster_priority_module = cluster_priority_module
        self._cluster_buffer = cluster_buffer
        self._event_buffer = event_buffer

    def tick(self, cluster_callback):
        id = self._cluster_priority_module.get_priority_cluster(self._priority)
        # centroid = self._cluster_buffer.get_centroid(id)
        this_cluster = self._event_buffer.get_cluster_locations(id)
        if len(this_cluster[0]) > 0:
            centroid = np.average(this_cluster, 1)
            cluster_callback(id, centroid)