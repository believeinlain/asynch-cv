
from sys import stdout
import cv2
import numpy as np

class basic_consumer:
    '''
    Basic consumer class that simply displays all events.
    Override this class to define alternative event processing functionality
    '''
    def __init__(self, width, height):
        '''
        Constructor
        '''
        self.width = width
        self.height = height
        # Names used to register as PythonConsumer with Metavision Designer
        self.mv_frame_gen_name = "FrameGen"
        self.mv_cd_prod_name = "CDProd"
        # store the current frame to display with OpenCV.imshow(self.frame)
        self.frame_to_draw = np.zeros((height, width, 3))
        self.frame_producer_output = None

    def metavision_event_callback(self, ts, src_events, src_2d_arrays):
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
        # If we have a frame producer, get that frame
        if self.mv_frame_gen_name in src_2d_arrays:
            # the shape of the frame in the analog buffer
            buffer_shape = src_2d_arrays[self.mv_frame_gen_name][0]
            # make sure the frames are the right size (height, width, rgb)
            assert buffer_shape == [self.height, self.width, 3], 'Frame generator producing frames of incorrect shape'
            # the actual analog buffer data
            frame_buffer = src_2d_arrays[self.mv_frame_gen_name][2]
            # convert the frame data into a format compatible with OpenCV
            self.frame_producer_output = frame_buffer.squeeze()

        # Prepare events for processing
        if self.mv_cd_prod_name in src_events:
            # the actual event buffer data
            event_buffer = src_events[self.mv_cd_prod_name][2]
            # make sure we're producing the correct array format
            assert event_buffer.dtype.names == ('x','y','p','t'), 'Unknown event buffer format'
            # appropriately process the events
            self.process_event_array(ts, event_buffer)

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
            for e in event_buffer:
                self.draw_event(e)
        
        stdout.write('Processeed %i events'%(len(event_buffer)))
        stdout.flush()
    
    def init_frame(self, frame_buffer=None):
        # if we have a frame_buffer, start with that
        if frame_buffer is not None:
            # assume greyscale framebuffer and repeat color channels
            self.frame_to_draw = np.repeat(frame_buffer, 3, 2)
        # otherwise fill frame with grey
        else:
            self.frame_to_draw = np.full((self.height, self.width, 3), 0.5)
    
    def draw_event(self, e):
        '''
        Draw event of the form ('x','y','p','t')
        '''
        color = e[2]*255
        self.frame_to_draw[e[1], e[0], :] = (color, color, color)

    def draw_frame(self):
        '''
        Called from main thread to display frame
        '''
        cv2.imshow('Events Display OpenCV', self.frame_to_draw)

    def end(self):
        '''
        This function will be called when execution has finished (i.e. no more events to process)
        '''
