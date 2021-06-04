
import numpy as np
from PMD.ClusterBuffer import *

class ClusterPriorityModule:
    def __init__(self, cluster_buffer: ClusterBuffer, types=None):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._cluster_id_t = types.get('cluster_id_t', 'u2')

        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._max_clusters = self._unassigned + 1

        self._cluster_buffer = cluster_buffer
        self._cluster_priorities = np.zeros(self._max_clusters, dtype=self._cluster_id_t)

    def tick(self):
        self._cluster_priorities = self._cluster_buffer.get_weight_order()

    def get_next_target(self):
        for id in self._cluster_priorities:
            if not self._cluster_buffer.is_tracking(id):
                self._cluster_buffer.track_cluster(id)
                return id
        
        return self._unassigned
