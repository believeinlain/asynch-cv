
import numpy as np

class EventBuffer:
    def __init__(self, width, height, depth, types):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._timestamp_t = types.get('timestamp_t', 'u8')
        self._cluster_id_t = types.get('cluster_id_t', 'u2')
        self._cluster_weight_t = types.get('cluster_weight_t', 'u4')
        self._buffer_depth_t = types.get('buffer_depth_t', 'u1')

        # Initialize
        self._unassigned = np.iinfo(np.dtype(self._cluster_id_t)).max
        self._max_clusters = self._unassigned + 1
        self._ts_buffer = np.zeros((width, height, depth), dtype=self._timestamp_t)
        self._id_buffer = np.full((width, height, depth), self._unassigned, dtype=self._cluster_id_t)
        self._top = np.zeros((width, height), dtype=self._buffer_depth_t)
        self._width = width
        self._height = height
        self._depth = depth

    # look in the vicinity of (x, y), count nearby events and get all nearby clusters
    def check_vicinity(self, x, y, t, tf, tc):
        # clip indices to the edges of the buffer
        x_range = slice(max(x-1, 0), min(x+2, self._width))
        y_range = slice(max(y-1, 0), min(y+2, self._height))

        ts_buffer_slice = self._ts_buffer[x_range, y_range, :]
        id_buffer_slice = self._id_buffer[x_range, y_range, :]
        # count the number of correlated events within tf
        num_correlated = np.count_nonzero(ts_buffer_slice > t-tf)
        # get a sorted list of nearby cluster ids
        clusters = np.unique(id_buffer_slice[ts_buffer_slice > t-tc])[:-1]

        return num_correlated, clusters
    
    def get_flat_id_buffer(self):
        top = np.transpose(np.squeeze(np.take_along_axis(self._id_buffer, self._top[:, :, np.newaxis], axis=2)))
        assigned = np.nonzero(top!=self._unassigned)
        return top, assigned

    def get_ts_buffer_top(self, x=None, y=None):
        return self._id_buffer[x, y, self._top[x, y]]

    def add_event(self, x, y, t, cluster=None):
        self._top[x, y] = (self._top[x, y] + 1) % self._depth

        if self._id_buffer[x, y, self._top[x, y]] == self._unassigned:
            u_ids = np.array([])
            u_x = np.array([])
            u_y = np.array([])
        else:
            u_ids = np.array([self._id_buffer[x, y, self._top[x, y]]])
            u_x = np.array([x])
            u_y = np.array([y])

        self._ts_buffer[x, y, self._top[x, y]] = t
        self._id_buffer[x, y, self._top[x, y]] = self._unassigned if cluster is None else cluster

        return u_ids, u_x, u_y

    def remove_expired_events(self, domain, t):
        x_range, y_range = domain
        
        ts_buffer_slice = self._ts_buffer[x_range, y_range, :]
        id_buffer_slice = self._id_buffer[x_range, y_range, :]

        expired = ts_buffer_slice < t
        assigned = id_buffer_slice != self._unassigned
        to_remove = np.where(np.logical_and(expired, assigned))

        u_ids = np.array(id_buffer_slice[to_remove], copy=True)
        
        id_buffer_slice[to_remove] = self._unassigned

        self._id_buffer[x_range, y_range, :] = id_buffer_slice

        u_x = np.add(x_range.start, to_remove[0])
        u_y = np.add(y_range.start, to_remove[1])

        return u_ids, u_x, u_y

    def get_cluster_map(self, id):
        return np.any(self._id_buffer == id, 2)

    def merge_clusters(self, ids):
        target = ids[0]
        others = ids[1:]

        # print("assigned ", others, "to ", target)

        for id in others:
            # print("id", id, "buffer", self._id_buffer[self._id_buffer == id])
            self._id_buffer[self._id_buffer == id] = target
