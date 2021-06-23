from os.path import join, expanduser
from play_file import play_file
from event_processing import basic_consumer, pmd_consumer

data_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'
annot_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'

data_format = '.aedat4'
annot_format = '.xml'

group = 'april_12'

boat_tests = [
    '25mm-1000us-speedboat-2021_04_12_15_09_24',
    '25mm-1200us-drifting-boat-2021_04_12_15_33_47',
    '75mm-1500us-drifting-boat-2021_04_12_15_35_24',
    '75mm-2000us-boat2-2021_04_12_15_21_16',
    '75mm-2000us-boat3-2021_04_12_15_30_50',
    '75mm-2000us-filter-boat-2021_04_12_15_16_43',
    '75mm-2000us-on-off-filter-boat-2021_04_12_15_17_24',
    '75mm-2000us-speedboat-2021_04_12_15_26_01'
]
annotations = [
    '25mm-1000us-speedboat-2021_04_12_15_09_24-2021_06_03_18_58_28-cvat+for+video+1.1',
    '25mm-1200us-drifting-boat-2021_04_12_15_33_47-2021_06_03_21_30_33-cvat+for+video+1.1',
    '75mm-1500us-drifting-boat-2021_04_12_15_35_24-2021_06_03_21_50_58-cvat+for+video+1.1',
    '75mm-2000us-boat2-2021_04_12_15_21_16-2021_06_03_22_21_59-cvat+for+video+1.1',
    '75mm-2000us-boat3-2021_04_12_15_30_50-2021_06_03_22_55_50-cvat+for+video+1.1',
    '75mm-2000us-filter-boat-2021_04_12_15_16_43-2021_06_03_23_20_19-cvat+for+video+1.1',
    '75mm-2000us-on-off-filter-boat-2021_04_12_15_17_24-2021_06_03_23_26_34-cvat+for+video+1.1',
    '75mm-2000us-speedboat-2021_04_12_15_26_01-2021_06_07_15_08_31-cvat+for+video+1.1'
]

for test in range(8):

    filename = join(group, boat_tests[test])
    run_name = f'{group}_run_{test:02d}'

    data_path = join(expanduser('~\\'), data_root, join(group, boat_tests[test]))+data_format
    annot_path = join(expanduser('~\\'), annot_root, join(group, annotations[test]))+annot_format

    play_file(
        filename=data_path,
        dt=33,
        event_consumer=pmd_consumer,
        consumer_args={
            'run_name': run_name,
            'annot_file': annot_path,
            # 'video_out': run_name+'.avi',
            'filetype': data_format,
            'targets': ['vessel', 'boat', 'RHIB'],
            'parameters': {
                'x_div': 4, # number of horizontal divisions
                'y_div': 4, # number of vertical divisions
                'us_per_event': 50, # processing time alloted to each event handler to process events
                'temporal_filter': 100_000,
                'event_buffer_depth': 8, # number of events to remember for each (x, y) position
                'tf': 250_000, # how far back in time to consider events for filtering
                'tc': 250_000, # how far back in time to consider events for clustering
                'n': 3, # minimum number of correlated events required to allow a particular event through the filter
                'max_cluster_size': 30, # maximum taxicab dist from center of cluster to each event
                'buffer_flush_period': 10_000, # microseconds periodicity to flush expired (>tc) events from buffer
                'num_analyzers': 12,

                'sample_period': 100_000, # microseconds between each centroid position sample
                'long_duration': 4_000_000, # microsecond duration to record samples for each cluster
                'short_duration': 2_000_000,

                'ratio_threshold': 75
            }
        })
