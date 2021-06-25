"""Simple test of basic_consumer functionality"""

from play_file import play_file
from event_processing.basic_consumer import basic_consumer

# data_path = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\april_29\\'
# filename = 'out_2021-04-29_18-02-48.raw'
# path = os.path.join(os.path.expanduser('~\\'), data_path, filename)

# path = data_path

# path = 'example_data/Cars_sequence.aedat4'
path = 'example_data/hand_spinner.raw'
run_name = 'test_basic_consumer'

args = {
    'run_name': run_name,
    'video_out': False
}

play_file(path, 30, basic_consumer, args)
