
from random import randint
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
        self._cluster_color_t = types.get('cluster_color_t', 'u1')
        self._xy_t = types.get('xy_t', 'u2')

        # Initialize
        self._event_buffer_t = [
            ('birth', self._timestamp_t), 
            ('weight', self._cluster_weight_t),
            ('color', self._cluster_color_t, (3,)),
            ('x_sum', self._xy_t),
            ('y_sum', self._xy_t)
            ]
        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._max_clusters = self._unassigned + 1
        self._clusters = np.zeros(self._max_clusters, dtype=self._event_buffer_t)
        # pick a different color for each region
        for i in range(self._max_clusters):
            self._clusters[i]['color'] = np.multiply(255.0, 
                hsv_to_rgb((i*np.pi % 3.6)/3.6, 1.0, 1.0), casting='unsafe')
    
    def get_birth_order(self, clusters):
        return np.argsort(self._clusters[clusters]['birth'])
    
    def get_color(self, id):
        return (0, 0, 0) if (id is None) or (id is self._unassigned) else self._clusters[id]['color']

    def create_new_cluster(self, x, y, t):
        new_id = 0
        tries = 0
        # pick a random empty cluster
        while self._clusters[new_id]['weight'] > 0:
            tries += 1
            new_id = randint(1, self._unassigned)
            # don't get stuck here
            if tries > 100:
                print("\nClusterBuffer.create_new_cluster: Cluster buffer getting full, assigned event to existing cluster.")
                return new_id

        self._clusters[new_id]['birth'] = t
        self._clusters[new_id]['x_sum'] = 0
        self._clusters[new_id]['y_sum'] = 0
        
        return new_id
    
    def add_event(self, x, y, id):
        self._clusters[id]['weight'] += 1
        self._clusters[id]['x_sum'] += x
        self._clusters[id]['y_sum'] += y

        return self._clusters[id]['weight']
    
    def remove_event(self, x, y, id):
        self._clusters[id]['weight'] -= 1
        if self._clusters[id]['weight'] == 0:
            self._clusters[id]['x_sum'] = 0
            self._clusters[id]['y_sum'] = 0
        else:
            self._clusters[id]['x_sum'] -= x
            self._clusters[id]['y_sum'] -= y
        
        return self._clusters[id]['weight']
            