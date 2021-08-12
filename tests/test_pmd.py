"""Test of pmd_consumer functionality, with a selection of data."""

from os.path import join, expanduser
from async_cv.play_file import play_file
from async_cv.event_processing.pmd_consumer import pmd_consumer


data_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'
annot_root = 'OneDrive\\Documents\\NIWC\\NeuroComp\\boat_tests\\'

files = {
    'june_12': {
        'boat_tests': {
            2: 'Davis346red-2020-06-12T12-11-45-0700-0_Test_2.aedat4',
            3: 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3.aedat4',
            5: 'Davis346red-2020-06-12T12-24-03-0700-0_Test_5.aedat4',
            6: 'Davis346red-2020-06-12T12-25-39-0700-0_Test_6.aedat4'
        },
        'annotations': {
            2: 'Davis346red-2020-06-12T12-11-45-0700-0_Test_2.xml',
            3: 'Davis346red-2020-06-12T12-15-01-0700-0_Test_3.xml',
            5: 'Davis346red-2020-06-12T12-24-03-0700-0_Test_5.xml',
            6: 'Davis346red-2020-06-12T12-25-39-0700-0_Test_6.xml'
        },
        'data_format': '.aedat4'
    },
    'june_26': {
        'boat_tests': {
            # 2: 'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.aedat4',
            3: 'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3.aedat4',
            # 4: 'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4.aedat4',
            6: 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6.aedat4',
            9: 'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9.aedat4',
            21: 'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21.aedat4'
        },
        'annotations': {
            # 2: 'Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.xml',
            3: 'Davis346red-2020-06-26T12-27-39-0700-00000195-0_Test_3.xml',
            # 4: 'Davis346red-2020-06-26T12-28-38-0700-00000195-0_Test_4.xml',
            6: 'Davis346red-2020-06-26T12-30-20-0700-00000195-0_Test_6.xml',
            9: 'Davis346red-2020-06-26T12-32-12-0700-00000195-0_Test_9.xml',
            21: 'Davis346red-2020-06-26T13-22-40-0700-00000195-0_Test_21.xml'
        },
        'data_format': '.aedat4'
    },
    'april_12': {
        'boat_tests': {
            0: '25mm-1000us-speedboat-2021_04_12_15_09_24.aedat4',
            1: '25mm-1200us-drifting-boat-2021_04_12_15_33_47.aedat4',
            2: '75mm-1500us-drifting-boat-2021_04_12_15_35_24.aedat4',
            3: '75mm-2000us-boat2-2021_04_12_15_21_16.aedat4',
            4: '75mm-2000us-boat3-2021_04_12_15_30_50.aedat4',
            5: '75mm-2000us-filter-boat-2021_04_12_15_16_43.aedat4',
            6: '75mm-2000us-on-off-filter-boat-2021_04_12_15_17_24.aedat4',
            # 7: '75mm-2000us-speedboat-2021_04_12_15_26_01.aedat4'
        },
        'annotations': {
            0: '25mm-1000us-speedboat-2021_04_12_15_09_24-2021_06_03_18_58_28-cvat+for+video+1.1.xml',
            1: '25mm-1200us-drifting-boat-2021_04_12_15_33_47-2021_06_03_21_30_33-cvat+for+video+1.1.xml',
            2: '75mm-1500us-drifting-boat-2021_04_12_15_35_24-2021_06_03_21_50_58-cvat+for+video+1.1.xml',
            3: '75mm-2000us-boat2-2021_04_12_15_21_16-2021_06_03_22_21_59-cvat+for+video+1.1.xml',
            4: '75mm-2000us-boat3-2021_04_12_15_30_50-2021_06_03_22_55_50-cvat+for+video+1.1.xml',
            5: '75mm-2000us-filter-boat-2021_04_12_15_16_43-2021_06_03_23_20_19-cvat+for+video+1.1.xml',
            6: '75mm-2000us-on-off-filter-boat-2021_04_12_15_17_24-2021_06_03_23_26_34-cvat+for+video+1.1.xml',
            # 7: '75mm-2000us-speedboat-2021_04_12_15_26_01-2021_06_07_15_08_31-cvat+for+video+1.1.xml'
        }
    },
    # 'april_29': {
    #     1: 'out_2021-04-29_17-56-14.raw',
    #     2: 'out_2021-04-29_17-57-47.raw',
    #     3: 'out_2021-04-29_18-02-48.raw',
    #     4: 'out_2021-04-29_18-04-41.raw',
    #     5: 'out_2021-04-29_18-06-47.raw',
    #     6: 'out_2021-04-29_18-10-59.raw',
    #     7: 'out_2021-04-29_18-17-21.raw',
    #     8: 'out_2021-04-29_18-20-10.raw'
    # },
}

# Define PMD parameters
parameters = {
    'x_div': 4,  # number of horizontal divisions
    'y_div': 4,  # number of vertical divisions
    'us_per_event': 50,  # processing time alloted to each event handler to process events
    'temporal_filter': 100_000,
    # number of events to remember for each (x, y) position
    'event_buffer_depth': 8,
    'tf': 200_000,  # how far back in time to consider events for filtering
    'tc': 200_000,  # how far back in time to consider events for clustering
    'n': 4,  # minimum number of correlated events required to allow a particular event through the filter
    'max_cluster_size': 30,  # maximum taxicab dist from center of cluster to each event
    # microseconds periodicity to flush expired (>tc) events from buffer
    'buffer_flush_period': 20_000,
    'num_analyzers': 32,

    'sample_period': 100_000,  # microseconds between each centroid position sample
    'long_duration': 3_000_000, #5_000_000,
    'short_duration': 2_000_000, #3_000_000,

    'detection_tau': -0.002,
    
    'ratio_threshold': 0,
    'dot_ratio_threshold': 1,
    'ratio_stability_factor': 1.0,
    'dot_ratio_stability_factor': 220.0,
}

def run_one(group, test):
    run_name = f'{group}_run_{test:02d}'

    data_path = join(expanduser('~\\'), data_root, join(
        group, files[group]['boat_tests'][test]))
    annot_path = join(expanduser('~\\'), annot_root, join(
        group, files[group]['annotations'][test]))

    play_file(data_path, 33, pmd_consumer, 
        run_name=run_name, 
        video_out=True,
        targets=['vessel', 'boat', 'RHIB'], 
        annot_file=annot_path, 
        show_metrics=False,
        parameters=parameters
    )

def run_group(group):
    for test in files[group]['boat_tests'].keys():
            run_one(group, test)

def run_all():
    for group in files:
        run_group(group)

# run_all()
run_group('june_12')
# run_one('june_12', 6)
