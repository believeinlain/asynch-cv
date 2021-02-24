'''
Deprecated: function to read .npy files and play them.
Needs to be updated to work properly, but .npy files will not likely be used due to
space constraints
'''
import sys
import time
import numpy as np

import cv2

def play_npy(filename, dt, event_consumer, consumer_args=None):
    '''
    Function to play npy files with the given event consumer.

    Parameters:
        filename: Filename with relative or absolute path included
        dt: time for each frame in milliseconds
        event_consumer: class to feed events into
    '''
    # translate None into an empty dict
    if consumer_args == None: consumer_args = {}

    npyfile = open(filename, 'rb')
    _ = npyfile.seek(0)

    event_buffers = []
    while True:
        array = None
        try:
            array = np.load(npyfile)
        except ValueError as err:
            # we don't actually care about the error, this just means we're done
            del err
            break
        if array is not None:
            event_buffers.append(array)
    
    event_data = np.concatenate(event_buffers)

    dt_us = dt*1_000 # dt in microseconds
    timestamps = event_data[:, 3]
    num_events = event_data.shape[0]
    last_index = num_events-1
    frame_start = 0
    frame_end = 0
    ts = timestamps[0]

    consumer = event_consumer(width=640, height=480, **consumer_args)

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
        consumer.process_event_array(ts, event_data[frame_start:frame_end, :])
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
        sys.stdout.write('\rFrame time: %i/%i(ms) '%(actual_dt, dt))
        sys.stdout.flush()

    cv2.destroyAllWindows()