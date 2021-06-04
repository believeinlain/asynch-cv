'''
Simple test of basic_consumer functionality
'''

import os.path
from src import play_file
from src import event_processing

data_path = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\april_29\\'
filename = 'out_2021-04-29_17-56-14.raw'
path = os.path.join(os.path.expanduser('~\\'), data_path, filename)
# path='example_data/Cars_sequence.aedat4'
# path='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat'
# path='example_data/hand_spinner.raw'
run_name = 'test_basic_consumer'

play_file(
    filename=path,
    dt=30,
    event_consumer=event_processing.basic_consumer,
    consumer_args={
        'run_name': run_name,
        'video_out': run_name+'.avi'
    })