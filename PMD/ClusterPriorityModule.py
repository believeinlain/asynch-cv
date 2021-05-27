
import numpy as np
from PMD.ClusterBuffer import *

class ClusterPriorityModule:
    def __init__(self, cluster_buffer: ClusterBuffer, types=None):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._cluster_id_t = types.get('cluster_id_t', 'u2')

        self._cluster_buffer = cluster_buffer
        self._cluster_priorities = np.zeros(np.iinfo(np.dtype(self._cluster_id_t)).max+1, dtype=self._cluster_id_t)

    def tick(self):
        self._cluster_priorities = self._cluster_buffer.get_weight_order()
    
    def get_priority_cluster(self, priority):
        return self._cluster_priorities[priority]