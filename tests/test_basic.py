"""Simple test of basic_consumer functionality"""

import os
from async_cv.play_file import play_file
from async_cv.event_processing.basic_consumer import basic_consumer

data_path = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\june_12\\'
filename = 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3.aedat4'
annot_file = 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3.xml'
path = os.path.join(os.path.expanduser('~\\'), data_path, filename)
annot_path = os.path.join(os.path.expanduser('~\\'), data_path, annot_file)

# path = data_path

# path = 'example_data/Cars_sequence.aedat4'
# path = 'example_data/hand_spinner.raw'

play_file(path, 30, basic_consumer, 
    run_name='basic_consumer_events+frames+annot',
    annot_file=annot_path,
    video_out=True
)
