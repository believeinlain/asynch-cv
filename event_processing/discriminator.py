
from colorsys import hsv_to_rgb
import numpy as np
from event_processing import basic_consumer

region_index_type = np.uint8
region_type = np.dtype([
    ('weight', np.uint32),
    ('birth', np.uint32),
    ('centroid', np.uint16, 2)
])

class discriminator(basic_consumer):
    '''
    Consumer that collects events into distinct regions
    '''
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height)
        # initialize all locations as assigned to no region (-1)
        self.region_index = np.full((width, height), -1, region_index_type)
        # max number of regions (also should be -1 if dtype=region_index_type)
        self.max_regions = np.iinfo(region_index_type).max
        # initialize the array of regions to empty regions
        self.regions = np.zeros(self.max_regions, region_type)
        self.surface = np.zeros((width, height), np.uint32)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        # draw frames (if applicable)
        self.init_frame(frame_buffer)

        # process each event individually
        for (x, y, p, t) in event_buffer:
            # ignore repeated events in the same location
            if self.surface[x, y] + 50_000 < t:
                self.surface[x, y] = t
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
                    # if there is only one adjacent region
                    if adjacent.size == 1:
                        # assign this event to it
                        self.assign_event_to_region(adjacent[0], x, y, p, t)
                    # if there is more than one adjacent region
                    elif adjacent.size > 1:
                        # assign this event to the largest region
                        max_index = max(adjacent, key=lambda x: self.regions[x]['weight'])
                        self.assign_event_to_region(max_index, x, y, p, t)
                    # if there are zero adjacent regions
                    else:
                        # create a new region
                        assigned = self.create_region(x, y, p, t)
                # draw event now that we've assigned regions
                self.draw_event(x, y, p, t)

        # unassign locations with no recent updates
        for (i, j) in np.transpose(np.nonzero(self.surface > ts-50_000)):
            index = self.region_index[i, j]
            if index != self.max_regions:
                self.regions[index]['weight'] -= 1
                self.region_index[i, j] = self.max_regions

    def draw_event(self, x, y, p, t):
        del t
        # pick a unique color for each region index
        color = np.multiply(255, hsv_to_rgb(((self.region_index[x, y]*10*np.pi) % 360)/360, 0.5+0.5*p, 1))
        # update the frame
        self.frame_to_draw[y, x, :] = color

    def assign_event_to_region(self, index, x, y, p, t):
        del p
        self.region_index[x, y] = index
        # is this a new region?
        if self.regions[index]['weight'] == 0:
            self.regions[index]['birth'] = t
            self.regions[index]['centroid'] = (x, y)
        self.regions[index]['weight'] += 1

    def create_region(self, x, y, p, t):
        assigned = self.max_regions
        for new_index in range(self.max_regions):
            if self.regions[new_index]['weight'] == 0:
                assigned = new_index
                self.assign_event_to_region(new_index, x, y, p, t)
                break
        
        return assigned