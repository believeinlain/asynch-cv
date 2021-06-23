
from sys import stdout
import cv2
import numpy as np
import xmltodict
import os
import matplotlib.pyplot as plt

from bounding_box import BoundingBox, BBFormat, BBType
from evaluators.pascal_voc_evaluator import plot_precision_recall_curves, get_pascalvoc_metrics

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
        self.run_name = consumer_args.get('run_name', 'test')
        print(f'Starting run "{self.run_name}"')

        if 'video_out' in consumer_args:
            # create directories if necessary
            cwd = os.path.abspath(os.getcwd())
            try:
                os.mkdir(f'{cwd}\\output\\')
            except FileExistsError:
                pass

            video_out_filename = consumer_args['video_out']
    
            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_out = cv2.VideoWriter(f'output/{video_out_filename}', fourcc, 20, (width, height))
            
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

    def metavision_event_callback(self, ts, src_events, src_2d_arrays):
        del src_2d_arrays # we don't want to use a frame producer
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
            # repack the event buffer (spacing to fit 4-byte sections, polarity is essentially padding)
            event_buffer = np.array(event_buffer, dtype=[('x','u2'), ('y','u2'), ('p','i4'), ('t','u8')])
            # appropriately process the events
            self.process_buffers(ts, event_buffer)

    def process_buffers(self, ts, event_buffer, frame_buffer=None):
        '''
        Callback method to override to process events.
        
        Parameters:
            ts: This is the timestamp of the end of the buffer.
                All events included in this callback will have a timestamp strictly lower than ts
            event_buffer: Array of events as tuples of the form ('x','y','p','t')
            frame_buffer: Array of greyscale pixels if captured by a conventional image chip
        '''
        # make sure we're producing the correct array format
        assert event_buffer.dtype.names == ('x','y','p','t'), 'Unknown event buffer format'
        # draw the frame we received from frame_buffer
        self.init_frame(frame_buffer)
        # process events accordingly
        self.process_event_buffer(ts, event_buffer)

    def init_frame(self, frame_buffer=None):
        # if we have a frame_buffer, start with that
        if frame_buffer is not None:
            # assume greyscale framebuffer and repeat color channels
            self.frame_to_draw = np.repeat(frame_buffer, 3, 2)
        # otherwise fill frame with grey
        else:
            self.frame_to_draw = np.full((self.height, self.width, 3), 80, dtype=np.uint8)

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
            cv2.rectangle(self.frame_to_draw, (xtl, ytl), (xbr, ybr), color)
            cv2.putText(self.frame_to_draw, label, (xtl, ytl), cv2.FONT_HERSHEY_PLAIN,
                0.5, color, 1, cv2.LINE_AA)
            
            # store in easy-to-read format
            if any(target in label for target in self._targets) and 'difficult' not in label:
                self._ground_truth.append(BoundingBox(f'frame_{self.frame_count:03d}',
                    class_id='target', coordinates=(xtl, ytl, xbr, ybr), format=BBFormat.XYX2Y2))

        # ensure the frame is contiguous for C processing
        self.frame_to_draw = np.ascontiguousarray(self.frame_to_draw, dtype=np.uint8)
    
    def process_event_buffer(self, ts, event_buffer):
        # we don't care about ts
        del ts
        # draw events colored by polarity
        for e in event_buffer:
            color = e['p']*255
            self.frame_to_draw[e['y'], e['x'], 0] = color
            self.frame_to_draw[e['y'], e['x'], 1] = color
            self.frame_to_draw[e['y'], e['x'], 2] = color

    def draw_frame(self):
        '''
        Called from main thread to display frame
        '''
        # display the frame on screen
        # cv2.imshow(self.run_name, self.frame_to_draw)
        cv2.imshow('run', self.frame_to_draw)
        
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

        # evaluate metrics
        metrics = get_pascalvoc_metrics(self._ground_truth, self._detections, 0.05)
        plot_precision_recall_curves(metrics['per_class'], savePath=f'metrics\\{self.run_name}',
            showAP=True, showInterpolatedPrecision=True, showGraphic=False)

    def save_detection(self, conf, bb):
        # bb should be in x y w h format
        self._detections.append(BoundingBox(f'frame_{self.frame_count:03d}',
            class_id='target', coordinates=bb, format=BBFormat.XYWH,
            bb_type=BBType.DETECTED, confidence=conf))
