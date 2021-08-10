

import os
from sys import stdout
import cv2
import numpy as np
import xmltodict
from time import time

from async_cv.event_processing.draw_events import draw_events


class basic_consumer:
    """Basic consumer class that simply displays all events. \
    Override this class to define new event processing functionality
    """

    def __init__(self, width: int, height: int, run_name='test',
                 video_out=False, **kwargs):
        """Constructor

        Args:
            width (int): Width of event sensor in pixels
            height (int): Height of event sensor in pixels
            run_name (str): Name of this run for output file naming
            video_out (bool): Produce an avi file composed of displayed frames
            annot_file (str): Path to annotation file to read to display \
                ground truth annotations
        """
        # store the current frame to display with OpenCV.imshow(self.frame)
        self._frame_to_draw = np.zeros((height, width, 3), dtype=np.uint8)

        self._frame_count = 0
        self._events_this_frame = 0

        # initialize annotation vars
        self._annotations = []
        self._annotations_version = {}
        self._annotations_meta = {}
        self._output_video = None

        self._run_name = run_name
        print('Starting run', run_name)

        # create output directories if necessary
        if not os.path.isdir(f'output/{self._run_name}/'):
            os.makedirs(f'output/{self._run_name}/')

        # if we want to output video
        if video_out:
            video_out_filename = run_name+'.avi'

            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self._output_video = cv2.VideoWriter(
                f'output/{self._run_name}/{video_out_filename}', 
                fourcc, 20, (width, height))

            print(f'Saving video file \"output/{self._run_name}/{video_out_filename}\"')

            if not os.path.isdir(f'output/{self._run_name}/frames/'):
                os.makedirs(f'output/{self._run_name}/frames/')

        if 'annot_file' in kwargs:
            try:
                with open(kwargs['annot_file']) as fd:
                    doc = xmltodict.parse(fd.read())
                    annot = doc['annotations']
                    self._annotations_version = annot['version']
                    self._annotations_meta = annot['meta']
                    if type(annot['track']) is list:
                        self._annotations = annot['track']
                    else:
                        self._annotations = [annot['track']]
            except FileNotFoundError:
                print(f'Annotation file "{kwargs["annot_file"]}" not found.')

    def metavision_event_callback(self, ts, src_events, src_2d_arrays):
        """Function to pass as a callback to use as an event consumer with 
            Metavision Designer.

        Args:
            ts: This is the timestamp of the end of the buffer. \
                All events included in this callback will have a timestamp \
                strictly lower than ts
            src_events: Dictionary containing a list for each component \
                associated with the PythonConsumer. \
                The label of each item in the dictionary is the name passed \
                when adding a new source to the PythonConsumer.
            src_2d_arrays: Frame producer output. Will be ignored.
        """
        # ignore frame producer output and timestamp
        del src_2d_arrays, ts
        # Prepare events for processing
        if 'CDProd' in src_events:
            # the actual event buffer data
            event_buffer = src_events['CDProd'][2]
            # appropriately process the events
            self.process_buffers(event_buffer)

    def process_buffers(self, event_buffer, frame_buffer=None):
        """Callback method to override to process events and frames.

        Args:
            event_buffer: Array of events as tuples of the form \
                ('x','y','p','t').
            frame_buffer: Array of greyscale pixels if captured by a \
                conventional image chip.
        
        """
        # draw the frame we received from frame_buffer
        self.init_frame(frame_buffer)
        # process events accordingly
        self.process_event_buffer(event_buffer)

    def init_frame(self, frame_buffer=None):
        # if we have a frame_buffer, start with that
        if frame_buffer is not None:
            # assume greyscale framebuffer and repeat color channels
            self._frame_to_draw = np.repeat(frame_buffer, 3, 2)
        # otherwise fill frame with grey
        else:
            self._frame_to_draw.fill(80)

        # read annotations
        for i in range(len(self._annotations)):
            box_frames = list(self._annotations[i]['box'])
            label = self._annotations[i]['@label']
            color = (200, 200, 200)

            # sync properly by frame number
            is_in_frame = False
            for box in box_frames:
                if int(box['@frame']) == self._frame_count:
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
            cv2.putText(self._frame_to_draw, label, (xtl, ytl),
                        cv2.FONT_HERSHEY_PLAIN, 0.5, color, 1, cv2.LINE_AA)

        # ensure the frame is contiguous for C processing
        self._frame_to_draw = np.ascontiguousarray(
            self._frame_to_draw, dtype=np.uint8)

    def process_event_buffer(self, ts, event_buffer):
        """Callback method to override to process events and frames.

        Args:
            event_buffer: Array of events as tuples of the form \
                ('x','y','p','t').
        
        """
        start = time()

        # draw events colored by polarity
        draw_events(self._frame_to_draw, event_buffer)

        ms = (time() - start)*1000.0

        stdout.write(f' Processed {len(event_buffer)} events in {ms:.0f}ms.')
        stdout.flush()

    def draw_frame(self):
        """Called from main thread to display frame"""

        # display the frame on screen
        cv2.imshow(self._run_name, self._frame_to_draw)

        # write the frame to the output avi
        if self._output_video is not None:
            self._output_video.write(self._frame_to_draw)

        cv2.imwrite(
            f'output/{self._run_name}/frames/frame_{self._frame_count}.jpg',
            self._frame_to_draw)

        self._frame_count += 1
        stdout.write(f' Frame: {self._frame_count:3}')
        stdout.flush()

    def end(self):
        """This function will be called when execution has finished \
            (i.e. no more events to process)
        """
        print('\nEnded playback')

        # wrap up the output video
        if self._output_video is not None:
            self._output_video.release()

        # finish displaying events
        cv2.destroyAllWindows()
