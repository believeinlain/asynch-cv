'''
Simple test of basic_consumer functionality
'''

import os.path
from play_file import play_file
from event_processing import basic_consumer

# data_path = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\april_29\\'
data_path = "example_data/hand_spinner.raw"
filename = 'out_2021-04-29_18-02-48.raw'
# path = os.path.join(os.path.expanduser('~\\'), data_path, filename)
path = data_path
# path='example_data/Cars_sequence.aedat4'
# path='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat'
# path='example_data/hand_spinner.raw'
run_name = 'test_basic_consumer'

play_file(
    filename=path,
    dt=30,
    event_consumer=basic_consumer,
    consumer_args={
        'run_name': run_name,
        'video_out': run_name+'.avi'
    })