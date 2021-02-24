'''
Simple test of filter_consumer functionality
'''
import event_player
import event_processing

event_player.play_file(
    # filename='example_data/hand_spinner.raw',
    filename='example_data/Cars_sequence.aedat4',
    # filename='example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat',
    dt=30,
    event_consumer=event_processing.filter_consumer,
    consumer_args= {
        'event_filter': event_processing.basic_filter,
        'filter_args': {'threshold': 100000}
    }
)
