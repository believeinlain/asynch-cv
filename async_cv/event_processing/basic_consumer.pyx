
import os
from sys import stdout
import cv2
import numpy as np
cimport numpy as np
import xmltodict
from time import time

cdef struct event:
    unsigned short x, y
    short p
    long long t

class basic_consumer:
    """Basic consumer class that simply displays all events.
    Override this class to define alternative event processing functionality
    """
    def __init__(self, width, height, consumer_args=None):
        """Constructor"""
        # store the current frame to display with OpenCV.imshow(self.frame)
        self._frame_to_draw = np.zeros((height, width, 3), dtype=np.uint8)
        
        self.frame_count = 0
        self.events_this_frame = 0

        if consumer_args is None:
            consumer_args = {}

        # what kind of objects will we check against?
        self._targets = consumer_args.get('targets', ['vessel'])

        # ground truth gathered from annotations
        self._ground_truth = []
        # detections to collect if objects are detected
        self._detections = []

        # process consumer args
        self.annotations = []
        self.annotations_version = {}
        self.annotations_meta = {}
        self.video_out = None

        self._run_name = consumer_args.get('run_name', 'test')
        print(f'Starting run "{self._run_name}"')

        self.show_metrics = consumer_args.get('show_metrics', False)

        # create directories if necessary
        if not os.path.isdir('output'):
            os.makedirs('output')

        if 'video_out' in consumer_args and consumer_args['video_out']:
            video_out_filename = self._run_name+'.avi'
    
            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_out = cv2.VideoWriter(f'output/{video_out_filename}', fourcc, 20, (width, height))

            print(f'Saving video file \"output/{video_out_filename}\"')
            
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
                print(f'Annotation file "{consumer_args["annot_file"]}" not found.')

    def metavision_event_callback(self, ts, src_events, src_2d_arrays):
        """Function to pass as a callback to use as an event consumer with 
            Metavision Designer.

        Args:
            ts: This is the timestamp of the end of the buffer.
                All events included in this callback will have a timestamp 
                strictly lower than ts
            src_events: Dictionary containing a list for each component 
                associated with the PythonConsumer.
                The label of each item in the dictionary is the name passed 
                when adding a new source to the PythonConsumer.
            src_2d_arrays: Frame producer output. Will be ignored.
        """
        # ignore frame producer output
        del src_2d_arrays 
        # Prepare events for processing
        if "CDProd" in src_events:
            # the actual event buffer data
            event_buffer = src_events["CDProd"][2]
            # appropriately process the events
            self.process_buffers(ts, event_buffer)

    def process_buffers(self, ts, event_buffer, frame_buffer=None):
        """Callback method to override to process events.
        
        Args:
            ts: This is the timestamp of the end of the buffer.
                All events included in this callback will have a timestamp 
                strictly lower than ts.
            event_buffer: Array of events as tuples of the form 
                ('x','y','p','t').
            frame_buffer: Array of greyscale pixels if captured by a 
                conventional image chip.
        """
        # draw the frame we received from frame_buffer
        self.init_frame(frame_buffer)
        # process events accordingly
        self.process_event_buffer(ts, event_buffer)

    def init_frame(self, frame_buffer=None):
        # if we have a frame_buffer, start with that
        if frame_buffer is not None:
            # assume greyscale framebuffer and repeat color channels
            self._frame_to_draw = np.repeat(frame_buffer, 3, 2)
        # otherwise fill frame with grey
        else:
            self._frame_to_draw.fill(80)

        # read annotations
        for i in range(len(self.annotations)):
            box_frames = list(self.annotations[i]['box'])
            label = self.annotations[i]['@label']
            color = (200, 200, 200)

            # sync properly by frame number
            is_in_frame = False
            for box in box_frames:
                if int(box['@frame']) == self.frame_count:
                    is_in_frame = True
                    break
            if not is_in_frame:
                continue

            # read box info
            xtl = int(float(box['@xtl']))
            ytl = int(float(box['@ytl']))
            xbr = int(float(box['@xbr']))
            ybr = int(float(box['@ybr']))
            # draw box on frame
            cv2.rectangle(self._frame_to_draw, (xtl, ytl), (xbr, ybr), color)
            cv2.putText(self._frame_to_draw, label, (xtl, ytl), cv2.FONT_HERSHEY_PLAIN,
                0.5, color, 1, cv2.LINE_AA)

            # save the ground truth bb if applicable
            if hasattr(self, 'save_ground_truth'):
                self.save_ground_truth(label, xtl, ytl, xbr, ybr)

        # ensure the frame is contiguous for C processing
        self._frame_to_draw = np.ascontiguousarray(self._frame_to_draw, dtype=np.uint8)
    
    def process_event_buffer(self, ts, event[:] event_buffer):
        # we don't care about ts
        del ts

        cdef int num_events = len(event_buffer)
        cdef double start
        cdef double ms

        start = time()

        # draw events colored by polarity
        cdef event e
        cdef unsigned char color
        cdef np.ndarray[unsigned char, ndim=3] frame = self._frame_to_draw
        for i in range(num_events):
            e = event_buffer[i]
            color = e.p*255
            frame[e.y, e.x, 0] = color
            frame[e.y, e.x, 1] = color
            frame[e.y, e.x, 2] = color

        ms = (time() - start)*1000.0
        
        stdout.write(f' Processed {num_events} events in {ms:.0f}ms.')
        stdout.flush()

    def draw_frame(self):
        """Called from main thread to display frame"""

        # display the frame on screen
        cv2.imshow(self._run_name, self._frame_to_draw)
        
        # write the frame to the output avi
        if self.video_out is not None:
            self.video_out.write(self._frame_to_draw)
        
        self.frame_count += 1
        stdout.write(f' Frame: {self.frame_count:3}')
        stdout.flush()

    def end(self):
        """This function will be called when execution has finished 
            (i.e. no more events to process)
        """
        print('\nEnded playback')

        # wrap up the output video
        if self.video_out is not None:
            self.video_out.release()

        # finish displaying events
        cv2.destroyAllWindows()
