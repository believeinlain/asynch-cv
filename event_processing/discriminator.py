
from sys import stdout
from colorsys import hsv_to_rgb
from random import randint, random
from math import exp
import numpy as np
import cv2
from event_processing import basic_consumer

RegionIndex = np.uint16
UNASSIGNED_REGION = np.iinfo(RegionIndex).max


class discriminator(basic_consumer):
    '''
    Consumer that collects events into distinct regions
    '''

    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height)
        # initialize all locations as assigned to no region (-1)
        self.region_index = np.full((width, height), -1, RegionIndex)
        # initialize the arrays of regions to empty regions
        max_regions = np.iinfo(RegionIndex).max
        self.regions_weight = np.zeros(max_regions, np.uint32)
        self.regions_birth = np.zeros(max_regions, np.uint32)
        self.regions_analyzed = np.zeros(max_regions, np.uint32)
        self.regions_color = np.zeros((max_regions, 3), np.uint8)
        self.regions_centroid = np.zeros((max_regions, 2), np.uint16)
        self.regions_velocity = np.zeros((max_regions, 2), np.int32)
        # surface of raw input events
        self.surface = np.zeros((width, height), np.uint64)
        # surface of events that have passed filtering
        self.surface_filtered = np.zeros((width, height), np.uint64)

        # timestamp of previous frame
        self.last_ts = None

        # Define the codec and create VideoWriter object (fixed dt of 30)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('output.avi', fourcc, 30, (width, height))

        # parameters
        # timeframe of inactivity in a location to unassign events
        self.region_lifetime = 50_000
        # period with which regions are unassigned (average # events before each run)
        self.unassign_period = 100
        # minimum correlated events to allow an event through the filter
        self.filter_n = 3
        # timeframe to search for correlated events when filtering
        self.filter_dt = 50_000
        # range to search around each event for correlation and region grouping
        self.v_range = 1
        # minimum weight to consider region worth analyzing
        self.min_region_weight = 10
        # minimum time for a region to exist before we care
        self.min_region_life = 1_000
        # divide the field into locales of <= density_locale_size pixels
        self.locale_size = 500

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

        self.frame_count = 0
        if consumer_args is not None:
            self.frame_annotations = consumer_args['track']['box']
        else:
            self.frame_annotations = []

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

            if random() < 0.9*(1-exp(-0.3*self.locale_events_per_ms[locale_i])):
                continue

            # find indices for the vicinity of the current event
            x_range = np.arange(x-self.v_range, x+self.v_range +
                                1).clip(0, self.width-1)
            y_range = np.arange(y-self.v_range, y +
                                self.v_range+1).clip(0, self.height-1)
            vicinity = (x_range[:, np.newaxis], y_range)

            # update surface for all events
            self.surface[x, y] = t

            # draw filtered events in grey
            if not self.allow_event(self.filter_dt, self.filter_n, vicinity, x, y, p, t):
                self.draw_event(x, y, p, t, (150, 150, 150))
                continue

            # update filtered surface for allowed events
            self.surface_filtered[x, y] = t

            # unassign expired locations
            if randint(1, self.unassign_period) == 1:
                self.unassign_from_all_regions(ts)

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
                    sorted_indices = np.argsort(self.regions_weight[adjacent])
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
            color = self.regions_color[self.region_index[x, y]]
            self.draw_event(x, y, p, t, color)

        self.region_analysis(ts)
        self.last_ts = ts

        stdout.write('Processed %i events' % (event_buffer.size))
        stdout.flush()

    def draw_frame(self):
        box = self.frame_annotations[self.frame_count]
        xtl = int(float(box['@xtl']))
        ytl = int(float(box['@ytl']))
        xbr = int(float(box['@xbr']))
        ybr = int(float(box['@ybr']))
        cv2.rectangle(self.frame_to_draw, (xtl, ytl), (xbr, ybr), (1, 1, 1))

        super().draw_frame()
        self.out.write(self.frame_to_draw)
        self.frame_count += 1

    def end(self):
        super().end()
        self.out.release()

    def reevaluate_locales(self, dt):
        self.locale_events_per_ms = np.floor_divide(self.locale_acc, dt//1_000)
        self.locale_acc[:] = 0

    def region_analysis(self, ts):
        # find regions we care about
        big_enough = np.nonzero(self.regions_weight >
                                self.min_region_weight)[0]
        # old_enough = np.nonzero(
        #     self.regions_birth+self.min_region_life < ts)[0]
        # regions_of_interest = np.intersect1d(big_enough, old_enough)
        regions_of_interest = big_enough

        for region in regions_of_interest:
            # binary image representing all locations belonging to this region
            # for cv2 image processing analysis
            image = np.multiply(255, np.transpose(
                self.region_index == region), dtype=np.uint8)

            # get the region color
            color = tuple(self.regions_color[region].tolist())
            # find and draw the region centroid
            m = cv2.moments(image, True)
            c = np.array([m['m10']/m['m00'], m['m01']/m['m00']],
                         dtype=np.uint16)
            cv2.circle(self.frame_to_draw, tuple(c), 1, color, thickness=2)
            # get previous analysis values
            last_c = self.regions_centroid[region]
            last_ts = self.regions_analyzed[region]
            last_v = self.regions_velocity[region]
            # if the region was analysed since birth
            if last_ts > self.regions_birth[region]:
                # find and draw the region velocity
                v = np.multiply(100, np.subtract(c, last_c, dtype=np.int32))
                v = np.array(np.average((last_v, v), 0,
                                        (0.8, 0.2)), dtype=np.int32)
                endpoint = np.add(c, v).clip(
                    (0, 0), (self.width-1, self.height-1))
                # cv2.arrowedLine(self.frame_to_draw, tuple(
                #     c), tuple(endpoint), color, thickness=1)
                # update the region velocity
                self.regions_velocity[region] = v

            # find and draw the bounding box
            x, y, w, h = cv2.boundingRect(image)
            # cv2.rectangle(self.frame_to_draw, (x, y),
            #               (x+w, y+h), color, 1)

            # update region analysis results
            self.regions_analyzed[region] = ts
            self.regions_centroid[region] = c

    def draw_event(self, x, y, p, t, color=None):
        if color is None:
            super().draw_event(x, y, p, t)
        else:
            del t, p
            self.frame_to_draw[y, x, :] = color

    def assign_event_to_region(self, index, x, y, p, t):
        del p, t
        self.region_index[x, y] = index
        self.regions_weight[index] += 1

    def create_region(self, x, y, p, t):
        for new_index in range(self.regions_weight.size):
            # use first empty index
            if self.regions_weight[new_index] == 0:
                self.regions_birth[new_index] = t
                # pick a random color for the new region
                self.regions_color[new_index] = np.multiply(
                    255.0, hsv_to_rgb((new_index*np.pi % 3.6)/3.6, 1.0, 1.0), casting='unsafe')
                self.assign_event_to_region(new_index, x, y, p, t)
                return new_index

        return UNASSIGNED_REGION

    def combine_regions(self, target, regions):
        # get all locations covered by the combined regions
        combined_footprint = np.isin(self.region_index, regions).nonzero()

        # determine the values for the final region
        combined_weight = np.sum(self.regions_weight[regions])
        combined_birth = min(self.regions_birth[regions])
        combined_color = self.regions_color[target]

        # mark all locations covered by regions as belonging to the target region
        self.region_index[combined_footprint] = target
        # reset all regions weight to zero since they've been unassigned
        self.regions_weight[regions] = 0

        # set the target region to the new values
        self.regions_weight[target] = combined_weight
        self.regions_birth[target] = combined_birth
        self.regions_color[target] = combined_color

    def allow_event(self, dt, n, i, x, y, p, t):
        del x, y, p
        # find recent events at indices i

        def is_recent(time):
            return time+dt >= t
        # allow if n or more recent events in vicinity
        vicinity_count = np.count_nonzero(is_recent(self.surface[i]))
        return vicinity_count >= n

    def unassign_from_all_regions(self, ts):
        expired = self.surface_filtered < ts-self.region_lifetime
        # print("expired", expired)
        has_region = self.region_index != UNASSIGNED_REGION
        # print("has_region", has_region)
        locations_to_unassign = np.logical_and(expired, has_region)
        # print("locations_to_unassign", locations_to_unassign)

        # subtract unassigned events from affected region weights
        affected_regions, counts = np.unique(
            self.region_index[locations_to_unassign], return_counts=True)
        counts_to_subtract = np.array(counts, dtype=np.uint32)
        if counts_to_subtract.size > 0:
            self.regions_weight[affected_regions] -= counts_to_subtract

        # zero out birth time of empty regions
        self.regions_birth[self.regions_weight == 0] = 0

        # set unassigned locations in index array
        self.region_index[locations_to_unassign] = UNASSIGNED_REGION
