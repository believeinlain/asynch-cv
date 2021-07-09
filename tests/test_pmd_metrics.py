"""Example PMD metrics evaluation on a collection of files"""

from os.path import join, expanduser
from async_cv.play_file import play_file
from async_cv.event_processing.pmd_consumer import pmd_consumer

data_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'
annot_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'

data_format = '.aedat4'
annot_format = '.xml'

files = {
    'june_12': {
        'boat_tests': [
            'Davis346red-2020-06-12T12-11-45-0700-0_Test_2',
            'Davis346red-2020-06-12T12-15-01-0700-0_Test_3',
            'Davis346red-2020-06-12T12-24-03-0700-0_Test_5',
            'Davis346red-2020-06-12T12-25-39-0700-0_Test_6'
        ],
        'annotations': [
            'Davis346red-2020-06-12T12-11-45-0700-0_Test_2',
            'Davis346red-2020-06-12T12-15-01-0700-0_Test_3',
            'Davis346red-2020-06-12T12-24-03-0700-0_Test_5',
            'Davis346red-2020-06-12T12-25-39-0700-0_Test_6'
        ]
    },
    'june_26': {
        'boat_tests': [
            'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2',
            'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3',
            'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4',
            'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6',
            'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9',
            'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21'
        ],
        'annotations': [
            'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2',
            'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3',
            'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4',
            'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6',
            'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9',
            'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21'
        ]
    },
    'april_12': {
        'boat_tests': [
            '25mm-1000us-speedboat-2021_04_12_15_09_24',
            '25mm-1200us-drifting-boat-2021_04_12_15_33_47',
            '75mm-1500us-drifting-boat-2021_04_12_15_35_24',
            '75mm-2000us-boat2-2021_04_12_15_21_16',
            '75mm-2000us-boat3-2021_04_12_15_30_50',
            '75mm-2000us-filter-boat-2021_04_12_15_16_43',
            '75mm-2000us-on-off-filter-boat-2021_04_12_15_17_24',
            '75mm-2000us-speedboat-2021_04_12_15_26_01'
        ],
        'annotations': [
            '25mm-1000us-speedboat-2021_04_12_15_09_24-2021_06_03_18_58_28-cvat+for+video+1.1',
            '25mm-1200us-drifting-boat-2021_04_12_15_33_47-2021_06_03_21_30_33-cvat+for+video+1.1',
            '75mm-1500us-drifting-boat-2021_04_12_15_35_24-2021_06_03_21_50_58-cvat+for+video+1.1',
            '75mm-2000us-boat2-2021_04_12_15_21_16-2021_06_03_22_21_59-cvat+for+video+1.1',
            '75mm-2000us-boat3-2021_04_12_15_30_50-2021_06_03_22_55_50-cvat+for+video+1.1',
            '75mm-2000us-filter-boat-2021_04_12_15_16_43-2021_06_03_23_20_19-cvat+for+video+1.1',
            '75mm-2000us-on-off-filter-boat-2021_04_12_15_17_24-2021_06_03_23_26_34-cvat+for+video+1.1',
            '75mm-2000us-speedboat-2021_04_12_15_26_01-2021_06_07_15_08_31-cvat+for+video+1.1'
        ]
    }
}

args = {
    'targets': ['vessel', 'boat', 'RHIB'],
    'show_metrics': True,
    'parameters': {
        'x_div': 4,  # number of horizontal divisions
        'y_div': 4,  # number of vertical divisions
        'us_per_event': 100,  # processing time alloted to each event handler to process events
        'temporal_filter': 50_000,
        # number of events to remember for each (x, y) position
        'event_buffer_depth': 16,
        'tf': 200_000,  # how far back in time to consider events for filtering
        'tc': 250_000,  # how far back in time to consider events for clustering
        'n': 4,  # minimum number of correlated events required to allow a particular event through the filter
        'max_cluster_size': 30,  # maximum taxicab dist from center of cluster to each event
        # microseconds periodicity to flush expired (>tc) events from buffer
        'buffer_flush_period': 10_000,
        'num_analyzers': 12,

        'sample_period': 100_000,  # microseconds between each centroid position sample
        'long_duration': 4_000_000,  # microsecond duration to record samples for each cluster
        'short_duration': 2_000_000,

        'ratio_threshold': 50
    }
}

parameters = {
    'x_div': 4,  # number of horizontal divisions
    'y_div': 4,  # number of vertical divisions
    'us_per_event': 100,  # processing time alloted to each event handler to process events
    'temporal_filter': 50_000,
    # number of events to remember for each (x, y) position
    'event_buffer_depth': 16,
    'tf': 200_000,  # how far back in time to consider events for filtering
    'tc': 250_000,  # how far back in time to consider events for clustering
    'n': 4,  # minimum number of correlated events required to allow a particular event through the filter
    'max_cluster_size': 30,  # maximum taxicab dist from center of cluster to each event
    # microseconds periodicity to flush expired (>tc) events from buffer
    'buffer_flush_period': 10_000,
    'num_analyzers': 12,

    'sample_period': 100_000,  # microseconds between each centroid position sample
    'long_duration': 4_000_000,  # microsecond duration to record samples for each cluster
    'short_duration': 2_000_000,

    'ratio_threshold': 50
}


def run_all():
    for group in files:
        for test in range(len(files[group]['boat_tests'])):
            run_one(group, test)


def run_one(group, test):
    run_name = f'{group}_run_{test:02d}'

    data_path = join(expanduser('~\\'), data_root, join(
        group, files[group]['boat_tests'][test]))+data_format
    annot_path = join(expanduser('~\\'), annot_root, join(
        group, files[group]['annotations'][test]))+annot_format

    play_file(
        data_path, 33, pmd_consumer, 
        run_name=run_name, 
        video_out=True,
        targets=['vessel', 'boat', 'RHIB'], 
        annot_file=annot_path, 
        parameters=parameters
    )


# run_one('april_12', 5)
run_all()
