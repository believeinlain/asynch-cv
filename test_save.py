'''
Simple test of basic_consumer functionality
'''
import event_player
import event_processing

event_player.play_metavision(
    filename='example_data/hand_spinner.raw',
    dt=30,
    event_consumer=event_processing.save_consumer,
    consumer_args= {
        'outfile': 'spinner.npy'
    }
)
