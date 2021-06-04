
from sys import stdout
import cv2
import numpy as np
import xmltodict
import os

import time

from src.event_processing import draw_events

class basic_consumer:
    '''
    Basic consumer class that simply displays all events.
    Override this class to define alternative event processing functionality
    '''
    def __init__(self, width, height, consumer_args=None):
        '''
        Constructor
        '''
        self.width = width
        self.height = height
        # Names used to register as PythonConsumer with Metavision Designer
        self.mv_frame_gen_name = "FrameGen"
        self.mv_cd_prod_name = "CDProd"
        # store the current frame to display with OpenCV.imshow(self.frame)
        self.frame_to_draw = np.zeros((height, width, 3), dtype=np.uint8)
        self.frame_producer_output = None
        
        self.frame_count = 0
        self.events_this_frame = 0

        # ground truth gathered from annotations
        self._ground_truth = []

        # process consumer args
        self.annotations = []
        self.annotations_version = {}
        self.annotations_meta = {}
        self.video_out = None
        self.run_name = 'test'
        if consumer_args is not None:
            self._consumer_args = consumer_args
            if 'run_name' in consumer_args:
                self.run_name = consumer_args['run_name']
                print(f'Starting run "{self.run_name}"')

            if 'video_out' in consumer_args:
                # create directories if necessary
                cwd = os.path.abspath(os.getcwd())
                try:
                    os.mkdir(f'{cwd}\\output\\')
                except FileExistsError:
                    pass

                video_out_filename = consumer_args['video_out']
        
                # Define the codec and create VideoWriter object (fixed dt of 30)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.video_out = cv2.VideoWriter(f'output/{video_out_filename}', fourcc, 30, (width, height))
            
            if 'annot_file' in consumer_args:
                try:
                    with open(consumer_args['annot_file']) as fd:
                        doc = xmltodict.parse(fd.read())
                        annot = doc['annotations']
                        self.annotations_version = annot['version']
                        self.annotations_meta = annot['meta']
                        if type(annot['track']) is list:
                            self.annotations = annot['track']
                        else:
                            self.annotations = [annot['track']]
                except FileNotFoundError:
                    print("Specified annotation file not found.")
                    pass
        else:
            self._consumer_args = {}

    def metavision_event_callback(self, ts, src_events, src_2d_arrays):
        del src_2d_arrays # we don't want to use a frame producer
        # tic = time.perf_counter()*1_000
        '''
        Function to pass as a callback to use as an event consumer with Metavision Designer.

        Parameters:
            ts: This is the timestamp of the end of the buffer.
                All events included in this callback will have a timestamp strictly lower than ts
            src_events: Dictionary containing a list for each component associated with the PythonConsumer.
                The label of each item in the dictionary is the name passed when adding a new source to the PythonConsumer.
                Each list is composed like this:
                    [0] contains the type of the events contained in this buffer. E.g. Event2d;
                    [1] contains the Numpy dtype information:
                            the size in bits of the event,
                            the name of each field,
                            the format of each field,
                            and their offset.
                        Note that the events are already decoded, so this information can be ignored;
                    [2] contains the array with the decoded events in this format (x, y, polarity, timestamp);
            src_2d_arrays: Contains similar information as the previous field.
                The composition of the list is slightly different:
                    [0] contains the array dimensions in the following format [width, height, channels];
                    [1] contains the Numpy dtype information of the pixel information;
                    [2] contains the 2D array data
        '''
        # Prepare events for processing
        if self.mv_cd_prod_name in src_events:
            # the actual event buffer data
            event_buffer = src_events[self.mv_cd_prod_name][2]
            # make sure we're producing the correct array format
            assert event_buffer.dtype.names == ('x','y','p','t'), 'Unknown event buffer format'
            # appropriately process the events
            self.process_event_array(ts, event_buffer)

        # toc = time.perf_counter()*1_000
        # print(f"Processed events in {toc - tic:0.4f} milliseconds")

    def process_event_array(self, ts, event_buffer, frame_buffer=None):
        '''
        Callback method to override to process events.
        
        Parameters:
            ts: This is the timestamp of the end of the buffer.
                All events included in this callback will have a timestamp strictly lower than ts
            event_buffer: Array of events as tuples of the form ('x','y','p','t')
            frame_buffer: Array of greyscale pixels if captured by a conventional image chip
        '''
        # ignore the timestamp for the default implementation
        del ts
        # if we have a frame from a frame_producer, we can draw that
        # (a "frame_producer" is Metavision's way of compiling events into frames.
        # if we want to do any event processing outside of Metavision Designer, we won't use this)
        if self.frame_producer_output is not None:
            self.frame_to_draw = self.frame_producer_output
        # otherwise just draw the events we received from event_buffer
        else:
            self.init_frame(frame_buffer)
            # draw events colored by polarity
            x_buffer = event_buffer['x'][:]
            y_buffer = event_buffer['y'][:]
            p_buffer = event_buffer['p'][:]
            self.frame_to_draw = draw_events.draw_events(
                self.frame_to_draw, len(event_buffer), x_buffer, y_buffer, p_buffer)
    
    def init_frame(self, frame_buffer=None):
        # if we have a frame_buffer, start with that
        if frame_buffer is not None:
            # assume greyscale framebuffer and repeat color channels
            self.frame_to_draw = np.repeat(frame_buffer, 3, 2)
        # otherwise fill frame with grey
        else:
            self.frame_to_draw = np.full((self.height, self.width, 3), 100, dtype=np.uint8)
        
        self._ground_truth.append([])

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
                
                # store in easy-to-read format
                self._ground_truth[self.frame_count].append({
                    'label': label,
                    'bb': (xtl, ytl, xbr, ybr)
                })

    def draw_frame(self):
        '''
        Called from main thread to display frame
        '''
        # display the frame on screen
        cv2.imshow(self.run_name, self.frame_to_draw)
        
        # write the frame to the output avi
        if self.video_out is not None:
            self.video_out.write(self.frame_to_draw)
        
        self.frame_count += 1
        stdout.write(f' Frame: {self.frame_count:3}')
        stdout.flush()

    def end(self):
        '''
        This function will be called when execution has finished (i.e. no more events to process)
        '''
        print('\nEnded playback')
        # wrap up the output video
        if self.video_out is not None:
            self.video_out.release()
