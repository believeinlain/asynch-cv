'''
Simple test of pmd_consumer functionality
'''
import os.path
from play_file import play_file
from event_processing import basic_consumer, pmd_consumer

run_name = 'test'

play_file(
filename='',
dt=33,
event_consumer=pmd_consumer,
consumer_args={
    'run_name': run_name,
    'video_out': run_name+'.avi',
    'parameters': {
        'x_div': 4, # number of horizontal divisions
        'y_div': 4, # number of vertical divisions
        'us_per_event': 100, # processing time alloted to each event handler to process events
        'event_buffer_depth': 4, # number of events to remember for each (x, y) position
        'tf': 250_000, # how far back in time to consider events for filtering
        'tc': 150_000, # how far back in time to consider events for clustering
        'n': 4, # minimum number of correlated events required to allow a particular event through the filter
        'max_cluster_size': 30, # maximum taxicab dist from center of cluster to each event
        'buffer_flush_period': 100_000, # microseconds periodicity to flush expired (>tc) events from buffer
        'num_analyzers': 12,

        'sample_period': 100_000, # microseconds between each centroid position sample
        'long_duration': 5_000_000, # microsecond duration to record samples for each cluster
        'short_duration': 3_000_000,

        'ratio_threshold': 100
    }
})
