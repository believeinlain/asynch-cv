
from collections import namedtuple
import numpy as np
from event_processing import basic_consumer

region_index_type = np.uint8
region_type = np.dtype([
    ('size', np.uint32),
    ('birth', np.uint32),
    ('centroid', np.uint16, 2)
])

class discriminator(basic_consumer):
    '''
    Consumer that collects events into distinct regions
    '''
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)
        # initialize all locations as assigned to no region (-1)
        self.region_index = np.full((width, height), -1, region_index_type)
        # max number of regions (also should be -1 if dtype=region_index_type)
        self.max_regions = np.iinfo(region_index_type).max
        # initialize the array of regions to empty regions
        self.regions = np.zeros(self.max_regions, region_type)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        # draw events and frames (if applicable)
        super().process_event_array(ts, event_buffer, frame_buffer)

        # process each event individually
        for (x, y, p, t) in event_buffer:
            # assign the event to the region it lands on
            assigned = self.region_index[x, y]
            # if the location was unassigned
            if assigned == self.max_regions:
                # search the vicinity for adjacent regions
                r = 1
                x_range = np.arange(x-r, x+r+1).clip(0, self.width-1)
                y_range = np.arange(y-r, y+r+1).clip(0, self.height-1)
                # get sorted list of unique region indices, sans -1 (-1 will be largest since unsigned)
                adjacent = np.unique(self.region_index[x_range[:, np.newaxis], y_range])[:-1]