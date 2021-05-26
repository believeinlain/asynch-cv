
import numpy as np

class EventBuffer:
    def __init__(self, width, height, depth, types):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._timestamp_t = types.get('timestamp_t', 'u8')
        self._cluster_id_t = types.get('cluster_id_t', 'u2')
        self._buffer_depth_t = types.get('buffer_depth_t', 'u1')

        # Initialize
        self._event_buffer_t = [('t', self._timestamp_t), ('c', self._cluster_id_t)]
        self._buffer = np.zeros((width, height, depth), dtype=self._event_buffer_t)
        self._top = np.zeros((width, height), dtype=self._buffer_depth_t)
        self._width = width
        self._height = height
        self._depth = depth
        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max

    # look in the vicinity of (x, y), count nearby events and get all nearby clusters
    def check_vicinity(self, x, y, t, tf, tc):
        # clip indices to the edges of the buffer
        x_range = slice(max(x-1, 0), min(x+2, self._width))
        y_range = slice(max(y-1, 0), min(y+2, self._height))

        buffer_slice = self._buffer[x_range, y_range, :]
        # count the number of correlated events within tf
        num_correlated = np.count_nonzero(buffer_slice['t'] > t-tf)
        # get a sorted list of nearby cluster ids
        clusters = np.unique(buffer_slice[buffer_slice['t'] > t-tc]['c'])[:-1]

        return (num_correlated, clusters)

    def add_event(self, x, y, t, cluster=None):
        self._top[x, y] = (self._top[x, y] + 1) % self._depth
        self._buffer[x, y, self._top[x, y]] = (t, self._unassigned if cluster is None else cluster)
