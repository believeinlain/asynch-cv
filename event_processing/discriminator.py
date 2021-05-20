
from sys import stdout
from math import exp
import numpy as np
import cv2
from numpy.lib import average
import xmltodict
import os

from event_processing import segmentation_filter

class discriminator(segmentation_filter):
    '''
    Consumer that discriminates regions based on characteristics
    and processes ground truth annotations for comparison
    '''
    def __init__(self, width, height, consumer_args=None):
        super().__init__(width, height, consumer_args)
        
        # initialize detection results
        self.detections = {}
        self.gts_images = []

        # process consumer args
        self.annotations = []
        self.annotations_version = {}
        self.annotations_meta = {}
        if consumer_args is not None:
            if 'annot_file' in consumer_args:
                with open(consumer_args['annot_file']) as fd:
                    doc = xmltodict.parse(fd.read())
                    annot = doc['annotations']
                    self.annotations_version = annot['version']
                    self.annotations_meta = annot['meta']
                    if type(annot['track']) is list:
                        self.annotations = annot['track']
                    else:
                        self.annotations = [annot['track']]
        else:
            consumer_args = {}

        # establish arrays to profile region movement over time
        self.profile_depth = consumer_args.get('profile_depth', 16)
        self.profile_centroids = np.zeros((self.max_regions, self.profile_depth, 2), np.float32)
        self.profile_timestamps = np.zeros((self.max_regions, self.profile_depth), np.uint64)
        self.profile_top = np.zeros((self.max_regions), np.uint8)
        self.draw_bb = consumer_args.get('draw_bb', True)
        self.region_boatness = np.zeros((self.max_regions), dtype=np.float32)
        self.region_displacement = np.zeros((self.max_regions, 2), np.float32)

        # create directories if necessary
        cwd = os.path.abspath(os.getcwd())
        try:
            os.mkdir(f'{cwd}\\metrics\\')
        except FileExistsError:
            pass
        
        try:
            os.mkdir(f'{cwd}\\metrics\\{self.run_name}\\')
        except FileExistsError:
            pass

        try:
            os.mkdir(f'{cwd}\\metrics\\{self.run_name}\\frames\\')
            os.mkdir(f'{cwd}\\metrics\\{self.run_name}\\detections\\')
            os.mkdir(f'{cwd}\\metrics\\{self.run_name}\\ground_truth\\')
            os.mkdir(f'{cwd}\\metrics\\{self.run_name}\\results\\')
        except FileExistsError:
            pass

    def init_frame(self, frame_buffer=None):
        super().init_frame(frame_buffer)
        image_name = f'frame_{self.frame_count:03d}.png'
        cv2.imwrite(f'metrics/{self.run_name}/frames/'+image_name, self.frame_to_draw)
        # convert annotations to image structure over track structure
        self.gts_images.append({
            '@id': str(self.frame_count),
            '@name': image_name,
            '@width': self.width,
            '@height': self.height,
            'box': []
        })
        # read annotations
        for i in range(len(self.annotations)):
            box_frames = list(self.annotations[i]['box'])
            label = self.annotations[i]['@label']
            color = (255, 255, 255) # tuple(int(label['color'][i:i+2], 16) for i in (1, 3, 5))
            if (self.frame_count < len(box_frames)):
                # read box info
                box = box_frames[self.frame_count]
                xtl = int(float(box['@xtl']))
                ytl = int(float(box['@ytl']))
                xbr = int(float(box['@xbr']))
                ybr = int(float(box['@ybr']))
                # draw box on frame
                cv2.rectangle(self.frame_to_draw, (xtl, ytl), (xbr, ybr), color)
                cv2.putText(self.frame_to_draw, label, (xtl, ytl), cv2.FONT_HERSHEY_PLAIN,
                    1, color, 1, cv2.LINE_AA)
                # add box to converted annotations
                # but only *boat*
                if 'boat' in label:
                    box['@label'] = 'boat'
                    self.gts_images[self.frame_count]['box'].append(box)

    def end(self):
        super().end()
        for filename in self.detections:
            with open(f'metrics/{self.run_name}/detections/'+filename,'w') as fd:
                fd.writelines(self.detections[filename])
        # correct the annotation meta
        self.annotations_meta['task']['mode'] = 'annotation'
        # stop at the last frame read
        self.annotations_meta['task']['size'] = self.frame_count+1
        self.annotations_meta['task']['stop_frame'] = self.frame_count
        # assume only one segment
        self.annotations_meta['task']['segments']['segment']['stop'] = self.frame_count
        with open(f'metrics/{self.run_name}/ground_truth/gts.xml','w') as fd:
            xmltodict.unparse({
                'annotations':{
                    'version': self.annotations_version,
                    'meta': self.annotations_meta,
                    'image':self.gts_images}
            }, output=fd)

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        super().process_event_array(ts, event_buffer, frame_buffer)
        self.region_analysis(ts)

    def region_analysis(self, ts):
        # find regions we care about
        big_enough = np.nonzero(self.regions_weight >
                                self.min_region_weight)[0]
        old_enough = np.nonzero(
            self.regions_birth+self.min_region_life < ts)[0]
        
        regions_of_interest = np.intersect1d(big_enough, old_enough)

        stdout.write(' %i regions of interest,' % (regions_of_interest.size))

        # buffer_ri_copy = self.buffer_ri.copy()
        # expired_buffer = np.nonzero(self.buffer_ts <= ts-self.region_lifetime)
        # buffer_ri_copy[expired_buffer] = self.unassigned_region

        for region in regions_of_interest:
            birth_time = self.regions_birth[region]
            # binary image representing all locations belonging to this region
            # for cv2 image processing analysis
            flat_region = np.any(self.buffer_ri == region, 2)
            image = np.multiply(255, np.transpose(flat_region), dtype=np.uint8)

            # find the region centroid
            this_region = np.nonzero(self.buffer_ri == region)[:-1]

            # print(c_x, c_y)
            c = np.average(this_region, 1)
            # print(c)
            int_c = tuple(np.array(c, dtype=np.uint16))

            # update region profile
            self.profile_top[region] = (self.profile_top[region] + 1) % self.profile_depth
            self.profile_timestamps[region, self.profile_top[region]] = ts
            self.profile_centroids[region, self.profile_top[region], :] = c

            if region in regions_of_interest:
                # get the region color
                color = tuple(self.regions_color[region].tolist())
                # draw the region centroid
                cv2.circle(self.frame_to_draw, int_c, 1, color, thickness=2)

                current = np.nonzero(self.profile_timestamps[region,:] >= birth_time)
                order = np.argsort(self.profile_timestamps[region, current][0])
                # past_timestamps = np.array(self.profile_timestamps[region, current][0, order], dtype=np.int64)
                past_locations = np.array(self.profile_centroids[region, current][0, order], dtype=np.float32)
                # dt = np.diff(past_timestamps)
                # dt_total = np.sum(dt, axis=0)
                path_steps = np.diff(past_locations, axis=0)
                if path_steps.size == 0:
                    continue

                # path = np.average(np.abs(path_steps), axis=0, weights=dt)
                path_length = np.sqrt(np.sum(np.square(path_steps)))
                displacement = np.sum(path_steps, axis=0)
                self.region_displacement[region] = displacement
                displacement_length = np.sqrt(np.sum(np.square(displacement)))

                if path_length == 0:
                    continue

                # for other_region in regions_of_interest:
                #     if region == other_region:
                #         continue
                #     rel_disp = np.sum(np.square(displacement - self.region_displacement[other_region]))
                #     rel_dist = np.sum(np.square(c - self.profile_centroids[other_region, self.profile_top[other_region], :]))
                #     if rel_disp < 0.1 and rel_dist < 50:
                #         print("MERGE REGIONS", region, other_region)

                scale = 10
                ratio_th = 1.8

                endpoint = np.sum([int_c, np.array(scale*(displacement/path_length), dtype=np.int16)], axis=0)
                cv2.arrowedLine(self.frame_to_draw, int_c, tuple(endpoint), color, thickness=1)

                cv2.circle(self.frame_to_draw, int_c, int(scale*ratio_th), color, thickness=1)

                if path_length != 0:
                    boatness_delta = (displacement_length/path_length)/ratio_th - 1
                    if (boatness_delta < 0 and self.region_boatness[region] > 0) or boatness_delta > 0:
                        self.region_boatness[region] += boatness_delta

                (is_boat, conf) = self.is_region_boat(region, ts)
                if is_boat:
                    # find and draw the bounding box
                    x, y, w, h = cv2.boundingRect(image)
                    
                    if self.draw_bb:
                        cv2.rectangle(self.frame_to_draw, (x, y),
                                    (x+w, y+h), color, 1)
                    cv2.putText(self.frame_to_draw, f'boat ({conf:0.2f})', (x, y), cv2.FONT_HERSHEY_PLAIN,
                                1, tuple(color), 1, cv2.LINE_AA)

                    # add it to detections
                    image_name = f'frame_{self.frame_count:03d}.txt'
                    box_str = f'boat {conf:0.2f} {int(x)} {int(y)} {int(w)} {int(h)}\n'
                    if not image_name in self.detections:
                        self.detections[image_name] = [box_str]
                    else:
                        self.detections[image_name].append(box_str)

    def create_region(self, x, y, p, t):
        region = super().create_region(x, y, p, t)
        if region != self.unassigned_region:
            self.region_boatness[region] = 0
            self.region_displacement[region] = 0
        
        return region

    def is_region_boat(self, region, ts):
        del ts
        tau = -0.08
        conf = 1 - exp(tau*self.region_boatness[region])
        return (conf > 0.5, conf)
