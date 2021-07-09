"""Simple test of pmd_consumer functionality from a live source"""

from async_cv.play_file import play_file
from async_cv.event_processing.pmd_consumer import pmd_consumer

play_file(
    filename='',
    dt=50,
    event_consumer=pmd_consumer,
    parameters={
        'x_div': 4,  # number of horizontal divisions
        'y_div': 4,  # number of vertical divisions
        'us_per_event': 500,  # processing time alloted to each event handler to process events
        # number of events to remember for each (x, y) position
        'event_buffer_depth': 4,
        'tf': 250_000,  # how far back in time to consider events for filtering
        'tc': 150_000,  # how far back in time to consider events for clustering
        'n': 4,  # minimum number of correlated events required to allow a particular event through the filter
        'max_cluster_size': 30,  # maximum taxicab dist from center of cluster to each event
        # microseconds periodicity to flush expired (>tc) events from buffer
        'buffer_flush_period': 100_000,
        'num_analyzers': 8,

        'sample_period': 100_000,  # microseconds between each centroid position sample
        'long_duration': 3_000_000,  # microsecond duration to record samples for each cluster
        'short_duration': 1_000_000,

        'ratio_threshold': 100
    }
)
