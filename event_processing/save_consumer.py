'''
Deprecated: consumer to save .npy files.
Needs to be updated to work properly, but .npy files will not likely be used due to
space constraints
'''
from event_processing import basic_consumer

import numpy as np

class save_consumer(basic_consumer):
    '''
    Consumer that saves events to disk as a numpy binary file.
    Each event_buffer is saved as a separate array for simplicity.
    '''
    def __init__(self, width, height, outfile):
        super().__init__(width, height)
        self.file = open(outfile, 'wb+')
        _ = self.file.seek(0)

    def process_event_array(self, ts, event_buffer):
        # display the events while saving
        super().process_event_array(ts, event_buffer)
        buffer_array = np.array(event_buffer.tolist())
        if len(buffer_array.shape)>1:
            np.save(self.file, buffer_array, allow_pickle=False)
    
    def end(self):
        # ensure the file is saved
        self.file.close()