"""Simple test of basic_consumer functionality"""

import os
from async_cv.play_file import play_file
from async_cv.event_processing.basic_consumer import basic_consumer

data_path = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\june_12\\'
filename = 'Davis346red-2020-06-12T12-24-03-0700-0_Test_5.aedat4'
path = os.path.join(os.path.expanduser('~\\'), data_path, filename)

# path = data_path

# path = 'example_data/Cars_sequence.aedat4'
# path = 'example_data/hand_spinner.raw'
run_name = 'test_basic_consumer'

args = {
    'run_name': run_name,
    'video_out': False
}

play_file(path, 30, basic_consumer, args)
