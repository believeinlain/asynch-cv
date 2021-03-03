
from colorsys import hsv_to_rgb
import numpy as np
from event_processing import basic_consumer

region_index_type = np.uint16
UNASSIGNED_REGION = np.iinfo(region_index_type).max
region_type = np.dtype([
    ('weight', np.uint32),
    ('birth', np.uint32),
    ('centroid', np.uint16, 2),
    ('color', np.uint8, 3)
])


class discriminator(basic_consumer):
    '''
    Consumer that collects events into distinct regions
    '''

    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height)
        # initialize all locations as assigned to no region (-1)
        self.region_index = np.full((width, height), -1, region_index_type)
        # initialize the array of regions to empty regions
        self.regions = np.zeros(np.iinfo(region_index_type).max, region_type)
        self.surface = np.zeros((width, height), np.uint32)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        # draw frames (if applicable)
        self.init_frame(frame_buffer)
        region_lifetime = 100_000
        filter_count = 5
        filter_dt = 20_000

        # process each event individually
        for (x, y, p, t) in event_buffer:
            # find indices for the vicinity of the current event
            r = 2
            x_range = np.arange(x-r, x+r+1).clip(0,
                                                 self.width-1)[:, np.newaxis]
            y_range = np.arange(y-r, y+r+1).clip(0, self.height-1)
            vicinity = (x_range, y_range)

            # update surface for all events
            self.update_surface(x, y, p, t)

            # ignore filtered events
            if not self.allow_event(filter_dt, filter_count, vicinity, x, y, p, t):
                continue

            # assign the event to the region it lands on
            assigned = self.region_index[x, y]

            # if the location was unassigned
            if assigned == UNASSIGNED_REGION:
                # get sorted list of unique region indices, sans 'unassigned'
                adjacent = np.unique(self.region_index[vicinity])[:-1]
                # if there is only one adjacent region
                if adjacent.size == 1:
                    # assign this event to it
                    self.assign_event_to_region(adjacent[0], x, y, p, t)
                # if there is more than one adjacent region
                elif adjacent.size > 1:
                    # find the largest region
                    sorted_indices = np.argsort(
                        self.regions[adjacent]['weight'])
                    largest_region = adjacent[sorted_indices][-1]
                    # merge all regions into the largest region
                    self.combine_regions(largest_region, adjacent)
                    # assign event to the largest region
                    self.assign_event_to_region(largest_region, x, y, p, t)
                # if there are zero adjacent regions
                else:
                    # create a new region
                    assigned = self.create_region(x, y, p, t)

            # draw event now that we've assigned regions
            self.draw_event(x, y, p, t)

        # unassign locations with no recent updates
        self.unassign_from_regions(ts, region_lifetime)

    def draw_event(self, x, y, p, t):
        del t, p
        (r, g, b) = self.regions[self.region_index[x, y]]['color']
        self.frame_to_draw[y, x, :] = (b, g, r)

    def update_surface(self, x, y, p, t):
        del p
        self.surface[x, y] = t

    def assign_event_to_region(self, index, x, y, p, t):
        del p, t
        self.region_index[x, y] = index
        self.regions[index]['weight'] += 1

    def create_region(self, x, y, p, t):
        for new_index in range(self.regions.size):
            # use first empty index
            if self.regions[new_index]['weight'] == 0:
                self.regions[new_index]['birth'] = t
                self.regions[new_index]['centroid'] = (x, y)
                # pick a random color for the new region
                self.regions[new_index]['color'] = np.multiply(
                    255.0, hsv_to_rgb(np.random.uniform(), 1.0, 1.0), casting='unsafe')
                self.assign_event_to_region(new_index, x, y, p, t)
                return new_index

        return UNASSIGNED_REGION

    def combine_regions(self, target, regions):
        # get all locations covered by the combined regions
        combined_footprint = np.isin(self.region_index, regions).nonzero()

        # determine the values for the final region
        combined_weight = np.sum(self.regions[regions]['weight'])
        combined_birth = min(self.regions[regions]['birth'])
        # just use the biggest for now
        combined_centroid = self.regions[target]['centroid']
        combined_color = self.regions[target]['color']

        # mark all locations covered by regions as belonging to the target region
        self.region_index[combined_footprint] = target

        # set the target region to the new values
        self.regions[target] = (
            combined_weight,
            combined_birth,
            combined_centroid,
            combined_color)

    def allow_event(self, dt, n, i, x, y, p, t):
        del x, y, p
        # find recent events at indices i

        def is_recent(time):
            return time+dt >= t
        # allow if n or more recent events in vicinity
        return np.count_nonzero(is_recent(self.surface[i])) >= n

    def unassign_from_regions(self, ts, dt):
        # unassign locations with no recent updates
        locations_to_unassign = np.nonzero(self.surface < ts-dt)
        for (i, j) in np.transpose(locations_to_unassign):
            index = self.region_index[i, j]
            if index != UNASSIGNED_REGION:
                if self.regions[index]['weight'] <= 1:
                    self.region_index[i, j] = -1
                    self.regions[index]['weight'] = 0
                else:
                    self.regions[index]['weight'] -= 1
