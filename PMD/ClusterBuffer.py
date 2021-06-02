
from random import randint, seed
from colorsys import hsv_to_rgb
import numpy as np

class ClusterBuffer:
    def __init__(self, types=None):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._timestamp_t = types.get('timestamp_t', 'u8')
        self._cluster_id_t = types.get('cluster_id_t', 'u2')
        self._cluster_weight_t = types.get('cluster_weight_t', 'u4')
        self._xy_t = types.get('xy_t', 'u2')
        self._xy_sum_t= types.get('xy_sum_t', 'u4')

        # Initialize
        self._cluster_buffer_t = [
            ('birth', self._timestamp_t), 
            ('weight', self._cluster_weight_t),
            ('x_sum', self._xy_sum_t),
            ('y_sum', self._xy_sum_t),
            ('is_tracking', '?')
            ]
        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._max_clusters = self._unassigned + 1
        self._clusters = np.zeros(self._max_clusters, dtype=self._cluster_buffer_t)

        seed(1)
    
    def get_birth(self, id):
        """Called by ClusterAnalyzer.tick to check tracked timestamps"""
        return self._clusters[id]['birth']
    
    def get_birth_order(self, clusters=None):
        """Called by EventHandler.tick to choose assignment for new events"""
        sort_birth = np.copy(self._clusters[clusters]['birth'])
        sort_birth[sort_birth == 0] = np.iinfo(np.dtype(self._timestamp_t)).max
        return np.argsort(sort_birth)

    def get_weight_order(self, clusters=None):
        """Called by ClusterPriorityModule.tick to determine priorities"""
        return np.flip(np.argsort(self._clusters[clusters]['weight'])[0])
    
    def get_centroid_f(self, id):
        """Called by ClusterAnalyzer.tick to track cluster movement"""
        weight = float(self._clusters[id]['weight'])
        if weight > 0.0:
            return (float(self._clusters[id]['x_sum'])/weight, 
                float(self._clusters[id]['y_sum'])/weight)
        else:
            print("\nClusterBuffer.get_centroid: Can't find centroid of empty cluster.")
            return (0.0, 0.0)

    def is_empty(self, id):
        """Called by ClusterAnalyzer.tick to check if cluster is empty"""
        return self._clusters[id]['weight'] == 0

    # TODO: There might be a bug here not letting region 0 die, or maybe just the seed?
    def create_new_cluster(self, t):
        """Called by EventHandler.tick to assign isolated events to a new cluster"""
        new_id = 0
        tries = 0
        # pick a random empty cluster
        while self._clusters[new_id]['weight'] > 0:
            tries += 1
            new_id = randint(1, self._unassigned-1)
            # don't get stuck here
            if tries > self._max_clusters//100:
                print("\nClusterBuffer.create_new_cluster: Cluster buffer getting full, assigned event to existing cluster.")
                return new_id

        self._clusters[new_id]['birth'] = t
        self._clusters[new_id]['x_sum'] = 0
        self._clusters[new_id]['y_sum'] = 0
        
        return new_id
    
    def add_event(self, x, y, id):
        """Called by EventHandler.tick to assign new events to a cluster"""
        self._clusters[id]['weight'] += 1
        self._clusters[id]['x_sum'] += x
        self._clusters[id]['y_sum'] += y
    
    def remove_events(self, ids, x, y):
        """Called by EventHandler.tick when events are displaced and to remove expired events"""
        for i in range(len(ids)):
            self._clusters[ids[i]]['weight'] -= 1
            self._clusters[ids[i]]['x_sum'] -= x[i]
            self._clusters[ids[i]]['y_sum'] -= y[i]
            if self._clusters[ids[i]]['weight'] == 0:
                self._clusters[ids[i]]['is_tracking'] = False

    def merge_clusters(self, ids):
        """Called by EventHandler.tick when merge_clusters is True and a new event bridges clusters"""
        target = ids[0]
        others = ids[1:]

        np.put(self._clusters['weight'], target, np.sum(self._clusters[ids]['weight']))
        np.put(self._clusters['x_sum'], target, np.sum(self._clusters[ids]['x_sum']))
        np.put(self._clusters['y_sum'], target, np.sum(self._clusters[ids]['y_sum']))

        np.put(self._clusters['weight'], others, 0)
        np.put(self._clusters['x_sum'], others, 0)
        np.put(self._clusters['y_sum'], others, 0)

    def track_cluster(self, id):
        self._clusters[id]['is_tracking'] = True

    def is_tracking(self, id):
        return self._clusters[id]['is_tracking']
