
import sys
import numpy as np
from PyAedatTools import ImportAedat

import cv2

from event_consumer import EventConsumer

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.
filename = 'example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat'
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

dt = 20000
timestamps = aedat['data']['polarity']['timeStamp']
num_events = len(timestamps)
last_index = num_events-1
frame_start = 0
frame_end = 0
ts = timestamps[0]

consumer = EventConsumer(width=346, height=260)

while True:
    # update time elapsed
    sys.stdout.write("\rTime %i" % ts)
    sys.stdout.flush()
    # advance frame by dt
    ts += dt
    # get indices for the current frame
    frame_end = np.searchsorted(timestamps[frame_start:], ts)
    # end if we run out of events
    print(' ',frame_end, last_index)
    if frame_end >= last_index:
        break
    # process buffered events into frame
    # print('start',frame_start, 'end',frame_end)
    consumer.process_event_array(ts, event_data[frame_start:frame_end,:])
    # draw frame with the events
    consumer.draw_frame()
    frame_start = frame_end
    # cv2.waitKey(int(dt/1000))

cv2.destroyAllWindows()