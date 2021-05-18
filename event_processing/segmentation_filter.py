
from sys import stdout
from colorsys import hsv_to_rgb
from random import randint, random
from math import exp
import numpy as np
from event_processing import basic_consumer

RegionIndex = np.uint16
UNASSIGNED_REGION = np.iinfo(RegionIndex).max
MAX_REGIONS = np.iinfo(RegionIndex).max

class segmentation_filter(basic_consumer):
    '''
    Consumer that collects events into distinct regions
    '''
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)
        self.unassigned_region = UNASSIGNED_REGION
        # initialize the arrays of regions to empty regions
        self.max_regions = MAX_REGIONS
        self.regions_weight = np.zeros(MAX_REGIONS, np.int64)
        self.regions_birth = np.zeros(MAX_REGIONS, np.uint64)
        self.regions_color = np.zeros((MAX_REGIONS, 3), np.uint8)
        # surface of raw input events
        self.surface = np.zeros((width, height), np.uint64)
        # surface of events that have passed filtering
        self.surface_filtered = np.zeros((width, height), np.uint64)

        # timestamp of previous frame
        self.last_ts = None

        # create empty dict if no args passed
        if consumer_args is None:
            consumer_args = {}

        # process consumer args
        # timeframe of inactivity in a location to unassign events
        self.region_lifetime = consumer_args.get('region_lifetime', 80_000)
        # minimum correlated events to allow an event through the filter
        self.filter_n = consumer_args.get('filter_n', 4)
        # timeframe to search for correlated events when filtering
        self.filter_dt = consumer_args.get('filter_dt', 100_000)
        # range to search around each event for correlation and region grouping
        self.v_range = consumer_args.get('v_range', 1)
        # minimum weight to consider region worth analyzing
        self.min_region_weight = consumer_args.get('min_region_weight', 20)
        # minimum time for a region to exist before we care
        self.min_region_life = consumer_args.get('min_region_life', 10_000)
        # divide the field into locales of <= density_locale_size pixels
        self.locale_size = consumer_args.get('locale_size', 500)

        # create event buffer for depth-based filtering
        self.buffer_depth = consumer_args.get('buffer_depth', self.filter_n)
        # buffer of raw input event timestamps
        self.buffer_ts = np.zeros((width, height, self.buffer_depth), np.uint64)
        # buffer of event region indices
        self.buffer_ri = np.full((width, height, self.buffer_depth), UNASSIGNED_REGION, RegionIndex)
        # index of the top of the buffer at each pixel
        self.buffer_top = np.zeros((width, height), np.uint8)

        # divide the field into locales
        div_n = 0
        self.div_width = self.width
        self.div_height = self.height
        while self.div_width*self.div_height > self.locale_size:
            div_n += 1
            self.div_width /= 2
            self.div_height /= 2

        self.locale_div = 2**div_n
        self.locale_acc = np.zeros(
            (self.locale_div, self.locale_div), np.uint64)
        self.locale_events_per_ms = np.zeros(
            (self.locale_div, self.locale_div), np.uint64)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        # init first frame ts
        if event_buffer.size == 0:
            return
        if self.last_ts is None:
            self.last_ts = event_buffer[0][3]

        # draw frames (if applicable)
        self.init_frame(frame_buffer)

        # reevaluate locale event density given time between frames
        self.reevaluate_locales(ts-self.last_ts)

        # process each event individually
        for (x, y, p, t) in event_buffer:
            # place event in locale buffer
            locale_i = (int(x/self.div_width), int(y/self.div_height))
            self.locale_acc[locale_i] += 1

            if random() < 0.95*(1-exp(-0.5*self.locale_events_per_ms[locale_i])):
                continue

            # find indices for the vicinity of the current event
            x_range = np.arange(x-self.v_range, x+self.v_range +
                                1).clip(0, self.width-1)
            y_range = np.arange(y-self.v_range, y +
                                self.v_range+1).clip(0, self.height-1)
            vicinity = (x_range[:, np.newaxis], y_range)

            # update surface for all events
            self.surface[x, y] = t

            # update buffer
            self.buffer_top[x, y] = (self.buffer_top[x, y] + 1) % self.buffer_depth
            self.buffer_ts[x, y, self.buffer_top[x, y]] = t

            # draw filtered events in grey
            if not self.allow_event(self.filter_dt, self.filter_n, vicinity, x, y, p, t):
                self.draw_event(x, y, p, t, (150, 150, 150))
                continue

            # update filtered surface for allowed events
            self.surface_filtered[x, y] = t

            # get sorted list of unique region indices from the buffer
            active_vicinity = np.nonzero(self.buffer_ts[vicinity] > t-self.region_lifetime)
            adjacent = np.unique(self.buffer_ri[vicinity][active_vicinity])[:-1]

            # if there is only one adjacent region
            if adjacent.size == 1:
                assigned = adjacent[0]
                # assign this event to it
                self.assign_event_to_region(adjacent[0], x, y, p, t)
            # if there is more than one adjacent region
            elif adjacent.size > 1:
                # find the region with most events adjacent to e
                count_adjacent = np.bincount(adjacent)
                sorted_indices = np.argsort(np.nonzero(count_adjacent))

                # assign event to region with most adjacent events
                assigned = adjacent[sorted_indices[0]][0]
                self.assign_event_to_region(assigned, x, y, p, t)
            # if there are zero adjacent regions
            else:
                # create a new region
                assigned = self.create_region(x, y, p, t)

            # draw event now that we've assigned regions
            color = self.regions_color[assigned]
            self.draw_event(x, y, p, t, color)

        # unassign expired regions
        expired_buffer = np.nonzero(self.buffer_ts <= ts-self.region_lifetime)
        self.buffer_ri[expired_buffer] = UNASSIGNED_REGION

        # recount weights for active regions
        active_buffer = np.nonzero(self.buffer_ts > ts-self.region_lifetime)
        active_regions = self.buffer_ri[active_buffer]
        self.regions_weight = np.bincount(active_regions, minlength=UNASSIGNED_REGION)
        unique_active_regions = np.unique(active_regions)[:-1]

        self.last_ts = ts

        stdout.write('Processed %i events,' % (event_buffer.size))
        stdout.write('%i/%i active regions,' % (unique_active_regions.size, MAX_REGIONS))
        stdout.flush()

    def reevaluate_locales(self, dt):
        self.locale_events_per_ms = np.floor_divide(self.locale_acc, dt//1_000)
        self.locale_acc[:] = 0

    def draw_event(self, x, y, p, t, color=None):
        if color is None:
            super().draw_event(x, y, p, t)
        else:
            del t, p
            self.frame_to_draw[y, x, :] = color

    def assign_event_to_region(self, index, x, y, p, t):
        del p, t
        self.regions_weight[index] += 1
        self.buffer_ri[x, y, self.buffer_top[x, y]] = index

    def create_region(self, x, y, p, t):
        # pick a random region index to assign
        # shouldn't be more then 2-3 tries since most regions are empty
        new_index = 0
        tries = 0
        while self.regions_weight[new_index] > 0:
            tries += 1
            new_index = RegionIndex(randint(0, MAX_REGIONS-1))
            # don't get stuck here
            if tries > 10:
                break

        # unused_indices = np.where(self.regions_weight == 0)[0]
        # if unused_indices.size > 0:
        #     new_index = unused_indices[0]
        #     # use first empty index
        #     if self.regions_weight[new_index] == 0:
        self.regions_birth[new_index] = t
        # pick a random color for the new region
        self.regions_color[new_index] = np.multiply(
            255.0, hsv_to_rgb((new_index*np.pi % 3.6)/3.6, 1.0, 1.0), casting='unsafe')
        self.assign_event_to_region(new_index, x, y, p, t)
        return new_index
        # else:
        #     return UNASSIGNED_REGION

    def allow_event(self, dt, n, i, x, y, p, t):
        del x, y, p
        # allow if n or more recent events in vicinity
        return np.count_nonzero(self.buffer_ts[i] >= t-dt) >= n
