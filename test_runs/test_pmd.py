'''
Simple test of pmd_consumer functionality
'''
import os.path
from play_file import play_file
from event_processing import pmd_consumer

data_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'
annot_root = './example_annotations/'

group = 'june_26'
test = 23
file_type = '.aedat4'

# group = 'april_29'
# test = 4
# file_type = '.raw'

# group = 'june_26'
# test = 2
# file_type = '.aedat4'

boat_tests = {
    'june_12':{
        1: 'Davis346red-2020-06-12T12-09-55-0700-0_Test_1',
        2: 'Davis346red-2020-06-12T12-11-45-0700-0_Test_2',
        3: 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3',
        5: 'Davis346red-2020-06-12T12-24-03-0700-0_Test_5',
        6: 'Davis346red-2020-06-12T12-25-39-0700-0_Test_6',
        # 9: 'Davis346red-2020-06-12T12-55-32-0700-0_Test_9',
        # 10: 'Davis346red-2020-06-12T12-58-00-0700-0_Test_10',
        # 13: 'Davis346red-2020-06-12T13-04-12-0700-0_Test_13'
    },
    'june_26':{
        # 1: 'Davis346red-2020-06-26T12-25-58-0700-00000195-0_Test_1',
        2: 'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2',
        3: 'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3',
        4: 'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4',
        # 5: 'Davis346red-2020-06-26T12-29-49-0700-00000195-0_Test_5',
        6: 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6',
        # 7: 'Davis346red-2020-06-26T12-30-41-0700-00000195-0_Test_7',
        # 8: 'Davis346red-2020-06-26T12-30-58-0700-00000195-0_Test_8',
        9: 'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9',
        # 16: 'Davis346red-2020-06-26T13-01-17-0700-00000195-0_Test_16',
        # 17: 'Davis346red-2020-06-26T13-03-06-0700-00000195-0_Test_17',
        # 19: 'Davis346red-2020-06-26T13-09-47-0700-00000195-0_Test_19',
        21: 'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21',
        # 23: 'Davis346red-2020-06-26T13-31-43-0700-00000195-0_Test_23'
    },
    'april_29':{
        1: 'out_2021-04-29_17-56-14',
        2: 'out_2021-04-29_17-57-47',
        3: 'out_2021-04-29_18-02-48',
        4: 'out_2021-04-29_18-04-41',
        5: 'out_2021-04-29_18-06-47',
        6: 'out_2021-04-29_18-10-59',
        7: 'out_2021-04-29_18-17-21',
        8: 'out_2021-04-29_18-20-10'
    }
}

for group in ['june_12', 'june_26']:

    all_runs = boat_tests[group].keys()
    # all_runs = [test]

    for test in all_runs:

        filename = os.path.join(group, boat_tests[group][test])
        run_name = f'{group}_run_{test:02d}'

        data_path = os.path.join(os.path.expanduser('~\\'), data_root, filename)+file_type
        annot_path = os.path.join(annot_root, filename)+'.xml'

        play_file(
            filename=data_path,
            dt=33,
            event_consumer=pmd_consumer,
            consumer_args={
                'run_name': run_name,
                'annot_file': annot_path,
                # 'video_out': run_name+'.avi',
                'filetype': file_type,
                'parameters': {
                    'x_div': 4, # number of horizontal divisions
                    'y_div': 4, # number of vertical divisions
                    'us_per_event': 100, # processing time alloted to each event handler to process events
                    'event_buffer_depth': 4, # number of events to remember for each (x, y) position
                    'tf': 250_000, # how far back in time to consider events for filtering
                    'tc': 150_000, # how far back in time to consider events for clustering
                    'n': 4, # minimum number of correlated events required to allow a particular event through the filter
                    'max_cluster_size': 30, # maximum taxicab dist from center of cluster to each event
                    'buffer_flush_period': 10_000, # microseconds periodicity to flush expired (>tc) events from buffer
                    'num_analyzers': 12,

                    'sample_period': 100_000, # microseconds between each centroid position sample
                    'long_duration': 5_000_000, # microsecond duration to record samples for each cluster
                    'short_duration': 3_000_000,

                    'ratio_threshold': 100,

                    # 'temporal_filter': 5_000,
                    # 'cluster_profile_length': 16,
                    # 'stability_threshold': 1.5,
                    # 'stability_loss_rate': 0.1,
                    # 'confidence_rate': 0.05,
                    # 'confidence_threshold': 0.5,
                    # 'merge_clusters': False
                }
            })
