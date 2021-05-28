
from PMD.EventStream import *
from PMD.InputQueue import *
from PMD.EventHandler import *
from PMD.EventBuffer import *
from PMD.ClusterBuffer import *
from PMD.ClusterPriorityModule import *
from PMD.ClusterAnalyzer import *


class PersistentMotionDetector:
    def __init__(self, width, height, parameters=None, types=None):
        # create empty dict if no types passed
        if types is None:
            types = {}
        # Set data types
        self._cluster_color_t = types.get('cluster_color_t', 'u1')
        # create empty dict if no parameters passed
        if parameters is None:
            parameters = {}
        self._x_div = parameters.get('x_div', 8)
        self._y_div = parameters.get('y_div', 8)
        self._input_queue_depth = parameters.get('input_queue_depth', 64)
        self._event_buffer_depth = parameters.get('event_buffer_depth', 4)
        self._num_cluster_analyzers = parameters.get('num_cluster_analyzers', 8)

        self._width = width
        self._height = height

        self._event_stream = EventStream(
            self._width, self._height, self._x_div, self._y_div, types)
        self._input_queue = np.array([[InputQueue(self._input_queue_depth)
                                       for _ in range(self._x_div)] for _ in range(self._y_div)], dtype=object)
        self._event_buffer = EventBuffer(
            self._width, self._height, self._event_buffer_depth, types)
        self._cluster_buffer = ClusterBuffer(types)
        d_width = self._width/self._x_div
        d_height = self._height/self._y_div
        domains = np.array(
            [[(slice(round(d_width*i), round(d_width*(i+1))),
                slice(round(d_height*j), round(d_height*(j+1))))
                for i in range(self._x_div)] for j in range(self._y_div)], dtype=object)
        self._event_handler = np.array(
            [[EventHandler(
                domains[i, j],
                self._input_queue[i, j],
                self._event_buffer,
                self._cluster_buffer,
                parameters)
              for i in range(self._x_div)] for j in range(self._y_div)], dtype=object)
        self._cluster_priority_module = ClusterPriorityModule(self._cluster_buffer, types)
        self._cluster_analyzers = np.array(
            [ClusterAnalyzer(i, self._cluster_priority_module, self._cluster_buffer, self._event_buffer) 
            for i in range(self._num_cluster_analyzers)], dtype=object)
    
    def process_events(self, event_buffer):
        # place events in their respective input queues
        dest = self._event_stream.place_events(event_buffer)
        for i in range(self._x_div):
            for j in range(self._y_div):
                events_to_push= np.intersect1d(np.where(dest[:,0] == i), np.where(dest[:,1] == j))
                self._input_queue[i, j].push_multiple(event_buffer[events_to_push])
    
    def tick_all(self, sys_time, event_callback, cluster_callback):
        # cycle through each event handler
        for i in range(self._x_div):
            for j in range(self._y_div):
                self._event_handler[i, j].tick(sys_time, event_callback)
        # run the cluster prioritizer
        self._cluster_priority_module.tick()
        # cycle through each cluster analyzer
        for analyzer in self._cluster_analyzers:
            analyzer.tick(sys_time, cluster_callback)
    
    def get_color(self, cluster_id):
        return self._cluster_buffer.get_color(cluster_id)

    def get_cluster_map(self):
        top, assigned = self._event_buffer.get_flat_id_buffer()
        return self._cluster_buffer.get_color(top[assigned]), assigned
    
    def get_single_cluster_map(self, id):
        footprint = self._event_buffer.get_cluster_map(id)
        return  np.multiply(255, footprint, dtype=self._cluster_color_t)

