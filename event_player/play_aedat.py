
import sys
import time
import numpy as np
from PyAedatTools import ImportAedat

import cv2

def play_aedat(filename, dt, event_consumer):
    '''
    Function to play aedat files with the given event consumer.

    Parameters:
        filename: Filename with relative or absolute path included
        dt: time for each frame in milliseconds
        event_consumer: class to feed events into
    '''

    # Create a dict with which to pass in the input parameters.
    aedat = {}
    aedat['importParams'] = {}

    # Put the filename, including full path, in the 'filePath' field.
    aedat['importParams']['filePath'] = filename

    # Invoke the import function
    aedat = ImportAedat.ImportAedat(aedat)

    # create data structure to process into frames
    event_data = np.array([ 
        aedat['data']['polarity']['x'],
        aedat['data']['polarity']['y'],
        aedat['data']['polarity']['polarity'],
        aedat['data']['polarity']['timeStamp']
    ]).transpose()

    dt_us = dt*1_000 # dt in microseconds
    timestamps = aedat['data']['polarity']['timeStamp']
    num_events = len(timestamps)
    last_index = num_events-1
    frame_start = 0
    frame_end = 0
    ts = timestamps[0]

    consumer = event_consumer(width=346, height=260)

    while True:
        # get real start time for current frame
        start_time = time.time_ns() // 1_000_000 # time in msec
        
        # get indices for the current frame
        [frame_start, frame_end] = np.searchsorted(timestamps, [ts, ts+dt_us])
        # advance frame by dt
        ts += dt_us
        # end if we run out of events
        if frame_end >= last_index:
            break
        # process buffered events into frame
        # print('start',frame_start, 'end',frame_end)
        consumer.process_event_array(ts, event_data[frame_start:frame_end,:], True, True)
        # draw frame with the events
        consumer.draw_frame()
        # wait until at least dt has elapsed
        end_time = time.time_ns() // 1_000_000 # time in msec
        end_of_frame = start_time + dt
        
        if end_time < end_of_frame:
            cv2.waitKey(end_of_frame-end_time)
            actual_dt = dt
        else:
            actual_dt = end_time-start_time
        
        # update time elapsed
        sys.stdout.write('\rFrame time:%i/%i(ms)'%(actual_dt, dt))
        sys.stdout.flush()

    cv2.destroyAllWindows()